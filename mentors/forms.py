from django import forms
from .models import Mentor, Availability


class AvailabilityForm(forms.ModelForm):

    class Meta:
        model = Availability
        fields = [
            "date",
            "start_time",
            "end_time",
        ]

        widgets = {
            "date": forms.DateInput(
                attrs={"type": "date"}
            ),

            "start_time": forms.TimeInput(
                attrs={"type": "time"}
            ),

            "end_time": forms.TimeInput(
                attrs={"type": "time"}
            ),
        }
class MentorProfileForm(forms.ModelForm):

    class Meta:
        model = Mentor

        fields = [
            "name",
            "expertise",
            "bio",
            "experience",
            "profile_image",
        ]

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "placeholder": "Your full name"
                }
            ),

            "expertise": forms.TextInput(
                attrs={
                    "placeholder": "e.g. Machine Learning & AI"
                }
            ),

            "bio": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": "Tell students about your experience..."
                }
            ),

            "experience": forms.NumberInput(
                attrs={
                    "min": 0,
                    "placeholder": "Years of experience"
                }
            ),

            "profile_image": forms.FileInput(),
        }