from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm
from workshops.models import Workshop
from queries.models import Session
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