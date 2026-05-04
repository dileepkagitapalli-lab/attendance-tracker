from django.db import models
from django.contrib.auth.models import AbstractUser

class Student(AbstractUser):
    roll_number = models.CharField(max_length=50, unique=True)
    branch = models.CharField(max_length=100)
    year = models.IntegerField(null=True, blank=True)
    semester = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} ({self.roll_number})"

class Timetable(models.Model):
    DAYS = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='timetables')
    day = models.CharField(max_length=10, choices=DAYS)
    time_slot = models.CharField(max_length=50)
    subject = models.CharField(max_length=100)
    duration = models.PositiveIntegerField(default=1)  # 1 unit = 1 hour, 2 units = 2 hours

    def __str__(self):
        return f"{self.student.roll_number} - {self.day} - {self.subject}"

class AttendanceRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    subject = models.CharField(max_length=100)
    time_slot = models.CharField(max_length=50)
    duration = models.PositiveIntegerField(default=1)
    attended = models.BooleanField(default=False)

    class Meta:
        unique_together = ('student', 'date', 'subject', 'time_slot')

    def __str__(self):
        status = "Present" if self.attended else "Absent"
        return f"{self.student.roll_number} - {self.date} - {self.subject} ({status})"

class ExtraClass(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='extra_classes')
    date = models.DateField()
    subject = models.CharField(max_length=100)
    time_slot = models.CharField(max_length=50)
    duration = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.student.roll_number} - {self.date} - {self.subject} (Extra)"

class SemesterInfo(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='semester_info')
    start_date = models.DateField()

    def __str__(self):
        return f"{self.student.roll_number} - Starts: {self.start_date}"

class WorkingDay(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='working_days')
    date = models.DateField()
    is_working_day = models.BooleanField(default=True)

    class Meta:
        unique_together = ('student', 'date')

    def __str__(self):
        status = "Working" if self.is_working_day else "Holiday"
        return f"{self.student.roll_number} - {self.date} - {status}"
