from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    )
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='student'
    )
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True
    )
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class Course(models.Model):
    title = models.CharField(max_length=200)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='courses/', blank=True, null=True)
    espace_depot = models.ForeignKey('EspaceDepot', on_delete=models.SET_NULL,
                                     null=True, blank=True)  # Use string reference

    def __str__(self):
        return self.title


class Assignment(models.Model):
    title = models.CharField(max_length=200)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    file = models.FileField(upload_to='assignments/', blank=True, null=True)

    def __str__(self):
        return self.title


class Submission(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, null=True, blank=True)  # Optional
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)  # Added
    file = models.FileField(upload_to='submissions/')
    grade = models.IntegerField(blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)

    def __str__(self):
        if self.assignment:
            return f"Submission by {self.student} for {self.assignment}"
        return f"Submission by {self.student} for {self.course}"


class EspaceDepot(models.Model):
    nom = models.CharField(max_length=200)
    matiere = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='espaces_depot', null=True, blank=True)

    def __str__(self):
        return self.nom


class StudentDashboardTime(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dashboard_times')
    time_spent = models.IntegerField(default=0)  # Time in minutes
    last_updated = models.DateTimeField(auto_now=True)  # Last time the record was updated

    def __str__(self):
        return f"{self.student.email} - {self.time_spent} minutes"

    @property
    def amount(self):
        return self.time_spent  # 1 minute = 1 dinar
