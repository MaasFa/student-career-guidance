from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Mentor, Availability
from .forms import AvailabilityForm
from workshops.models import Workshop
@login_required
def mentor_dashboard(request):

    mentor = Mentor.objects.get(
        user=request.user
    )

    availabilities = Availability.objects.filter(
        mentor=mentor
    ).order_by(
        "date",
        "start_time"
    )

    workshops = Workshop.objects.filter(
        mentor=mentor
    ).order_by(
        "date",
        "start_time"
    )

    return render(
        request,
        "mentors/mentor_dashboard.html",
        {
            "mentor": mentor,
            "availabilities": availabilities,
            "workshops": workshops,
        }
    )
@login_required
def add_availability(request):

    mentor = Mentor.objects.get(
        user=request.user
    )

    if request.method == "POST":

        form = AvailabilityForm(request.POST)

        if form.is_valid():

            availability = form.save(
                commit=False
            )

            availability.mentor = mentor
            availability.save()

            return redirect("mentor_dashboard")

    else:

        form = AvailabilityForm()

    return render(
        request,
        "mentors/add_availability.html",
        {
            "form": form
        }
    )
@login_required
def mentor_list(request):

    mentors = Mentor.objects.all()

    return render(
        request,
        "mentors/mentor_list.html",
        {
            "mentors": mentors
        }
    )


@login_required
def mentor_detail(request, mentor_id):

    mentor = get_object_or_404(
        Mentor,
        id=mentor_id
    )

    availabilities = Availability.objects.filter(
        mentor=mentor,
        is_available=True
    ).order_by(
        "date",
        "start_time"
    )

    return render(
        request,
        "mentors/mentor_detail.html",
        {
            "mentor": mentor,
            "availabilities": availabilities,
        }
    )