from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import get_template
from .models import Student, Timetable, AttendanceRecord, ExtraClass, SemesterInfo, WorkingDay
from django.contrib import messages
from django import forms
from datetime import date, datetime, timedelta

def format_time_12hr(t_str):
    if not t_str: return ""
    try:
        return datetime.strptime(t_str, '%H:%M').strftime('%I:%M %p')
    except (ValueError, TypeError):
        return t_str

def calculate_duration(start_time_str, end_time_str):
    try:
        t1 = datetime.strptime(start_time_str, '%H:%M')
        t2 = datetime.strptime(end_time_str, '%H:%M')
        delta = t2 - t1
        hours = round(delta.total_seconds() / 3600)
        return max(1, int(hours))
    except (ValueError, TypeError):
        return 1

def sort_by_time(entries):
    def get_start_time(entry):
        try:
            start_str = entry.time_slot.split(' - ')[0]
            return datetime.strptime(start_str.strip(), '%I:%M %p').time()
        except (ValueError, IndexError, AttributeError):
            from datetime import time
            return time(0, 0)
    return sorted(entries, key=get_start_time)
import calendar
from xhtml2pdf import pisa
from io import BytesIO
from openpyxl import Workbook

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'roll_number', 'branch', 'year', 'semester']

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data['roll_number']
            user.set_unusable_password()
            user.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('dashboard')
    else:
        form = RegistrationForm()
    return render(request, 'auth/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        roll_number = request.POST.get('roll_number')
        first_name = request.POST.get('first_name')
        
        user = Student.objects.filter(roll_number=roll_number, first_name__iexact=first_name).first()
        if user is not None:
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid Name or Roll Number")
    return render(request, 'auth/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    attendance_records = AttendanceRecord.objects.filter(student=request.user)
    subjects_stats = {}
    total_conducted = 0
    total_attended = 0
    timetable_subjects = request.user.timetables.values_list('subject', flat=True).distinct()
    extra_subjects = ExtraClass.objects.filter(student=request.user).values_list('subject', flat=True).distinct()
    all_subjects = set(list(timetable_subjects) + list(extra_subjects))

    for sub in all_subjects:
        sub_records = attendance_records.filter(subject=sub)
        sub_conducted = sum(r.duration for r in sub_records)
        sub_attended = sum(r.duration for r in sub_records if r.attended)
        perc = (sub_attended / sub_conducted * 100) if sub_conducted > 0 else 0
        needed_75 = 0
        if perc < 75:
            needed_75 = max(0, int(((0.75 * sub_conducted) - sub_attended) / 0.25 + 0.99))
        subjects_stats[sub] = {
            'conducted': sub_conducted,
            'attended': sub_attended,
            'percentage': round(perc, 2),
            'needed_75': needed_75,
            'warning': perc < 75 and sub_conducted > 0
        }
        total_conducted += sub_conducted
        total_attended += sub_attended

    overall_perc = (total_attended / total_conducted * 100) if total_conducted > 0 else 0
    sem_info = getattr(request.user, 'semester_info', None)
    days_passed = 0
    if sem_info:
        days_passed = (date.today() - sem_info.start_date).days

    context = {
        'stats': subjects_stats,
        'overall_perc': round(overall_perc, 2),
        'total_conducted': total_conducted,
        'total_attended': total_attended,
        'days_passed': days_passed,
        'warning_overall': overall_perc < 75 and total_conducted > 0
    }
    return render(request, 'attendance/dashboard.html', context)

@login_required
def subject_detail(request, subject_name):
    past_records = AttendanceRecord.objects.filter(
        student=request.user, subject=subject_name
    ).order_by('-date', '-id')
    
    timetables = request.user.timetables.filter(subject=subject_name)
    upcoming_classes = []
    
    if timetables.exists():
        current_date = date.today() + timedelta(days=1)
        count = 0
        max_lookahead = 60
        lookahead = 0
        
        while count < 5 and lookahead < max_lookahead:
            day_name = calendar.day_name[current_date.weekday()]
            day_slots = timetables.filter(day=day_name)
            
            if day_slots.exists():
                working_day = WorkingDay.objects.filter(student=request.user, date=current_date).first()
                if not working_day or working_day.is_working_day:
                    sorted_slots = sort_by_time(list(day_slots))
                    for slot in sorted_slots:
                        upcoming_classes.append({
                            'date': current_date,
                            'day': day_name,
                            'time_slot': slot.time_slot
                        })
                    count += 1
            
            current_date += timedelta(days=1)
            lookahead += 1
            
    context = {
        'subject_name': subject_name,
        'past_records': past_records,
        'upcoming_classes': upcoming_classes
    }
    return render(request, 'attendance/subject_detail.html', context)

@login_required
def timetable_manage(request):
    all_days = [d[0] for d in Timetable.DAYS]
    
    # Initialize wizard state
    if 'completed_days' not in request.session:
        request.session['completed_days'] = []
    
    completed_days = request.session['completed_days']
    
    # Determine current day
    requested_day = request.GET.get('day')
    if requested_day in all_days:
        current_day = requested_day
    else:
        current_day = None
        for day in all_days:
            if day not in completed_days:
                current_day = day
                break
        if not current_day:
            current_day = all_days[0] # Fallback to Monday if all are completed

    if request.method == 'POST':
        if 'mark_completed' in request.POST:
            day_to_complete = request.POST.get('day')
            if day_to_complete not in completed_days:
                completed_days.append(day_to_complete)
                request.session['completed_days'] = completed_days
                request.session.modified = True
            
            if len(completed_days) >= len(all_days):
                return redirect('timetable_summary')
            
            next_day = None
            for d in all_days:
                if d not in completed_days:
                    next_day = d
                    break
            
            from django.urls import reverse
            if next_day:
                return redirect(f"{reverse('timetable_manage')}?day={next_day}")
            return redirect('timetable_manage')
        else:
            # Retrieve day from POST data to ensure we stay on the same day
            posted_day = request.POST.get('day')
            if posted_day in all_days:
                current_day = posted_day
                
            start_time = request.POST.get('start_time')
            start_ampm = request.POST.get('start_ampm')
            end_time = request.POST.get('end_time')
            end_ampm = request.POST.get('end_ampm')
            
            time_slot = f"{start_time} {start_ampm} - {end_time} {end_ampm}"
            
            # Convert to 24h format for duration calculation
            try:
                t1 = datetime.strptime(f"{start_time} {start_ampm}", '%I:%M %p')
                t2 = datetime.strptime(f"{end_time} {end_ampm}", '%I:%M %p')
                delta = t2 - t1
                hours = round(delta.total_seconds() / 3600)
                duration = max(1, int(hours))
            except (ValueError, TypeError):
                duration = 1
            
            Timetable.objects.create(
                student=request.user,
                day=current_day,
                time_slot=time_slot,
                subject=request.POST.get('subject'),
                duration=duration
            )
            messages.success(request, f"Added {request.POST.get('subject')} to {current_day}")
            from django.urls import reverse
            return redirect(f"{reverse('timetable_manage')}?day={current_day}")
            
    timetables = request.user.timetables.filter(day=current_day)
    timetables = sort_by_time(list(timetables))
    
    context = {
        'timetables': timetables, 
        'current_day': current_day,
        'completed_days': completed_days,
        'all_days': all_days,
        'all_completed': len(completed_days) >= len(all_days)
    }
    return render(request, 'attendance/timetable.html', context)

@login_required
def timetable_summary(request):
    if request.method == 'POST':
        if 'confirm' in request.POST:
            if 'completed_days' in request.session:
                del request.session['completed_days']
            messages.success(request, "Timetable confirmed!")
            return redirect('dashboard')
        elif 'edit' in request.POST:
            if 'completed_days' in request.session:
                del request.session['completed_days']
            return redirect('timetable_manage')

    timetables = request.user.timetables.all()
    days_data = []
    for day in [d[0] for d in Timetable.DAYS]:
        day_entries = [t for t in timetables if t.day == day]
        day_entries = sort_by_time(day_entries)
        days_data.append({'day': day, 'entries': day_entries})

    return render(request, 'attendance/timetable_summary.html', {'days_data': days_data})

@login_required
def timetable_delete(request, pk):
    entry = request.user.timetables.get(pk=pk)
    day = entry.day
    entry.delete()
    messages.success(request, "Timetable entry removed")
    from django.urls import reverse
    return redirect(f"{reverse('timetable_manage')}?day={day}")

@login_required
def semester_info_update(request):
    if request.method == 'POST':
        SemesterInfo.objects.update_or_create(student=request.user, defaults={'start_date': request.POST.get('start_date')})
        messages.success(request, "Semester start date updated")
        return redirect('dashboard')
    info = getattr(request.user, 'semester_info', None)
    return render(request, 'attendance/semester_info.html', {'info': info})

@login_required
def mark_working_day(request):
    if request.method == 'POST':
        date_str = request.POST.get('date')
        is_working = request.POST.get('is_working') == 'yes'
        WorkingDay.objects.update_or_create(student=request.user, date=date_str, defaults={'is_working_day': is_working})
        from django.urls import reverse
        if is_working:
            return redirect(reverse('mark_attendance') + f"?date={date_str}")
        return redirect('dashboard')
    return redirect('dashboard')

@login_required
def extra_class_manage(request):
    if request.method == 'POST':
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        duration = calculate_duration(start_time, end_time)
        time_slot = f"{format_time_12hr(start_time)} - {format_time_12hr(end_time)}"
        ExtraClass.objects.create(
            student=request.user,
            date=request.POST.get('date'),
            subject=request.POST.get('subject'),
            time_slot=time_slot,
            duration=duration
        )
        messages.success(request, "Extra class added")
        return redirect('dashboard')
    return render(request, 'attendance/extra_class.html')

@login_required
def mark_attendance(request):
    date_str = request.GET.get('date')
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = date.today()
    else:
        selected_date = date.today()

    day_name = calendar.day_name[selected_date.weekday()]
    working_day = WorkingDay.objects.filter(student=request.user, date=selected_date).first()
    if not working_day:
        return render(request, 'attendance/mark_working_day_ask.html', {'date': selected_date})
    if not working_day.is_working_day:
        messages.info(request, f"The selected date ({selected_date}) is marked as a holiday.")
        return redirect('dashboard')

    regular_slots = sort_by_time(list(Timetable.objects.filter(student=request.user, day=day_name)))
    extra_slots = sort_by_time(list(ExtraClass.objects.filter(student=request.user, date=selected_date)))

    if request.method == 'POST':
        for slot in regular_slots:
            AttendanceRecord.objects.update_or_create(
                student=request.user, date=selected_date, subject=slot.subject, time_slot=slot.time_slot,
                defaults={'duration': slot.duration, 'attended': request.POST.get(f'reg_{slot.id}') == 'present'}
            )
        for slot in extra_slots:
            AttendanceRecord.objects.update_or_create(
                student=request.user, date=selected_date, subject=slot.subject, time_slot=slot.time_slot,
                defaults={'duration': slot.duration, 'attended': request.POST.get(f'extra_{slot.id}') == 'present'}
            )
        messages.success(request, f"Attendance marked successfully for {selected_date}!")
        return redirect('dashboard')

    return render(request, 'attendance/mark_attendance.html', {
        'date': selected_date, 'day_name': day_name, 'regular_slots': regular_slots, 'extra_slots': extra_slots
    })

@login_required
def attendance_calendar(request):
    events = [{'date': r.date.isoformat(), 'subject': r.subject, 'attended': r.attended} for r in AttendanceRecord.objects.filter(student=request.user)]
    holidays = [w.date.isoformat() for w in WorkingDay.objects.filter(student=request.user) if not w.is_working_day]
    return render(request, 'attendance/calendar.html', {'events': events, 'holidays': holidays})

def get_stats_context(user):
    attendance_records = AttendanceRecord.objects.filter(student=user)
    subjects_stats = {}
    total_conducted = total_attended = 0
    all_subjects = set(list(user.timetables.values_list('subject', flat=True).distinct()) + list(ExtraClass.objects.filter(student=user).values_list('subject', flat=True).distinct()))
    for sub in all_subjects:
        sub_records = attendance_records.filter(subject=sub)
        sub_conducted = sum(r.duration for r in sub_records)
        sub_attended = sum(r.duration for r in sub_records if r.attended)
        subjects_stats[sub] = {'conducted': sub_conducted, 'attended': sub_attended, 'percentage': round((sub_attended / sub_conducted * 100) if sub_conducted > 0 else 0, 2)}
        total_conducted += sub_conducted
        total_attended += sub_attended
    return {'user': user, 'stats': subjects_stats, 'overall_perc': round((total_attended / total_conducted * 100) if total_conducted > 0 else 0, 2), 'total_conducted': total_conducted, 'total_attended': total_attended, 'date': date.today()}

@login_required
def export_pdf(request):
    context = get_stats_context(request.user)
    template = get_template('attendance/report_pdf.html')
    html = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="attendance_report.pdf"'
        return response
    return HttpResponse("Error generating PDF", status=500)

@login_required
def export_excel(request):
    context = get_stats_context(request.user)
    wb = Workbook()
    ws = wb.active
    ws.title = "Attendance Report"
    ws.append(['Student Name', request.user.first_name])
    ws.append(['Roll Number', request.user.roll_number])
    ws.append(['Branch', request.user.branch])
    ws.append(['Generated On', str(date.today())])
    ws.append([])
    ws.append(['Subject', 'Total Classes (Units)', 'Attended (Units)', 'Percentage'])
    for sub, data in context['stats'].items():
        ws.append([sub, data['conducted'], data['attended'], f"{data['percentage']}%"])
    ws.append([])
    ws.append(['OVERALL', context['total_conducted'], context['total_attended'], f"{context['overall_perc']}%"])
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=attendance_report.xlsx'
    wb.save(response)
    return response
