from django import forms
from .models import StudentQuery
from .models import StudentQuery, Session

class StudentQueryForm(forms.ModelForm):

    class Meta:
        model = StudentQuery

        fields = [
            "name",
            "email",
            "subject",
            "topic",
            "query",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Your name"
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "placeholder": "Your email"
                }
            ),

            "subject": forms.TextInput(
                attrs={
                    "placeholder": "e.g. Machine Learning"
                }
            ),

            "topic": forms.TextInput(
                attrs={
                    "placeholder": "e.g. Random Forest"
                }
            ),

            "query": forms.Textarea(
                attrs={
                    "rows": 6,
                    "placeholder": (
                        "Describe your question or problem..."
                    )
                }
            ),
        }

class SessionScheduleForm(forms.ModelForm):

    class Meta:
        model = Session

        fields = [
            "date",
            "start_time",
            "end_time",
            "meeting_link",
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

            "meeting_link": forms.URLInput(
                attrs={
                    "placeholder": "https://meet.google.com/..."
                }
            ),
        }