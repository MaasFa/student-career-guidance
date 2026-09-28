from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from workshops.models import Workshop
from queries.models import Session
from .forms import RegisterForm, StudentProfileForm

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("login")

    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("dashboard")

    return render(request, "accounts/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


def dashboard_view(request):

    if request.user.profile.role == "mentor":
        return redirect("mentor_dashboard")

    workshops = Workshop.objects.filter(
        status="published"
    ).order_by(
        "date",
        "start_time"
    )[:6]

    sessions = Session.objects.filter(
        student=request.user,
        status="confirmed"
    ).order_by(
        "date",
        "start_time"
    )

    return render(
        request,
        "accounts/student_dashboard.html",
        {
            "workshops": workshops,
            "sessions": sessions,
        }
    )

@login_required
def profile_view(request):

    profile = request.user.profile

    if profile.role == "mentor":
        return redirect("mentor_profile")

    return render(
        request,
        "accounts/profile.html",
        {
            "profile": profile
        }
    )
@login_required
def edit_profile(request):

    profile = request.user.profile

    if profile.role == "mentor":
        return redirect("edit_mentor_profile")

    if request.method == "POST":

        form = StudentProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if form.is_valid():

            profile = form.save()

            request.user.first_name = form.cleaned_data.get(
                "first_name",
                request.user.first_name
            )

            request.user.last_name = form.cleaned_data.get(
                "last_name",
                request.user.last_name
            )

            request.user.email = form.cleaned_data["email"]

            request.user.save()

            return redirect("profile")

    else:

        form = StudentProfileForm(
            instance=profile,
            initial={
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "email": request.user.email,
            }
        )

    return render(
        request,
        "accounts/edit_profile.html",
        {
            "form": form
        }
    )