from django import forms
from .models import Course, Assignment, Submission, EspaceDepot, User


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'file', 'espace_depot']  # This should now work


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'course', 'file']


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['file']


class UserRegisterForm(forms.ModelForm):
    class Meta:
        model = User  # Adjust based on your custom User model
        fields = ['username', 'email', 'password', 'user_type']


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class GradingForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['grade', 'feedback']


class EspaceDepotForm(forms.ModelForm):
    class Meta:
        model = EspaceDepot
        fields = ['nom']
