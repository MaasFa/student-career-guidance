from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from mentors.models import Mentor
from workshops.models import Workshop
from .forms import WorkshopForm


@login_required
def create_workshop(request):

    mentor = Mentor.objects.get(
        user=request.user
    )

    if request.method == "POST":

        form = WorkshopForm(request.POST)

        if form.is_valid():

            workshop = form.save(
                commit=False
            )

            workshop.mentor = mentor

            workshop.save()

            return redirect("mentor_dashboard")

    else:
        form = WorkshopForm()

    return render(
        request,
        "workshops/create_workshop.html",
        {"form": form}
    )

@login_required
def workshop_list(request):

    workshops = Workshop.objects.filter(
        status="published"
    ).order_by(
        "date",
        "start_time"
    )

    return render(
        request,
        "workshops/workshop_list.html",
        {
            "workshops": workshops
        }
    )