from django import forms
from django.contrib.auth.models import User
from .models import Profile


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput
    )

    role = forms.ChoiceField(
        choices=Profile.ROLE_CHOICES
    )

    class Meta:
        model = User
        fields = ["username", "email", "password", "role"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()

            Profile.objects.create(
                user=user,
                role=self.cleaned_data["role"]
            )

        return user
class StudentProfileForm(forms.ModelForm):

    first_name = forms.CharField(
        max_length=100,
        required=False
    )

    last_name = forms.CharField(
        max_length=100,
        required=False
    )

    email = forms.EmailField()

    field_order = [
    "first_name",
    "last_name",
    "email",
    "profile_image",
    "education",
    "career_interest",
    "skills",
    "bio",
   ]
    class Meta:
            model = Profile
            fields = [
            "profile_image",
            "education",
            "career_interest",
            "skills",
            "bio",
            ]
            widgets = {
            "education": forms.TextInput(
                attrs={
                    "placeholder": "e.g. B.Tech Computer Science"
                }
            ),

            "career_interest": forms.TextInput(
                attrs={
                    "placeholder": "e.g. Machine Learning, AI, Data Science"
                }
            ),

            "skills": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Python, SQL, Machine Learning, Django..."
                }
            ),

            "bio": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Tell us a little about yourself..."
                }
            ),

            "profile_image": forms.FileInput(),
        }