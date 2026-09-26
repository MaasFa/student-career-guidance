from django import forms
from .models import Workshop


class WorkshopForm(forms.ModelForm):

    class Meta:
        model = Workshop

        fields = [
            "title",
            "topic",
            "description",
            "session_type",
            "date",
            "start_time",
            "duration",
            "meeting_link",
        ]

        widgets = {
            "date": forms.DateInput(
                attrs={"type": "date"}
            ),

            "start_time": forms.TimeInput(
                attrs={"type": "time"}
            ),

            "description": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": "Describe what students will learn..."
                }
            ),

            "duration": forms.NumberInput(
                attrs={
                    "min": 15,
                    "placeholder": "Duration in minutes"
                }
            ),

            "meeting_link": forms.URLInput(
                attrs={
                    "placeholder": "https://meet.google.com/..."
                }
            ),
        }