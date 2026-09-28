from django.contrib.auth.decorators import login_required

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from .models import Mentor, Availability

from .forms import (
    AvailabilityForm,
    MentorProfileForm
)

from workshops.models import Workshop

from queries.models import (
    StudentQuery,
    Session
)


# =====================================================
# MENTOR DASHBOARD
# =====================================================

@login_required
def mentor_dashboard(request):

    mentor = Mentor.objects.get(
        user=request.user
    )

    # Every published public lecture/workshop
    all_workshops = Workshop.objects.filter(
        status="published"
    ).select_related(
        "mentor"
    ).order_by(
        "date",
        "start_time"
    )

    # Current mentor's workshops
    my_workshops = Workshop.objects.filter(
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
            "all_workshops": all_workshops,
            "my_workshops": my_workshops,
        }
    )
# =====================================================
# ADD AVAILABILITY
# =====================================================

@login_required
def add_availability(request):

    mentor = Mentor.objects.get(
        user=request.user
    )

    if request.method == "POST":

        form = AvailabilityForm(
            request.POST
        )

        if form.is_valid():

            availability = form.save(
                commit=False
            )

            availability.mentor = mentor

            availability.save()

            return redirect(
                "mentor_dashboard"
            )

    else:

        form = AvailabilityForm()

    return render(
        request,
        "mentors/add_availability.html",
        {
            "form": form
        }
    )


# =====================================================
# MENTOR LIST
# =====================================================

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


# =====================================================
# MENTOR DETAIL
# =====================================================

@login_required
def mentor_detail(
    request,
    mentor_id
):

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


# =====================================================
# MY MENTOR PROFILE
# =====================================================

@login_required
def mentor_profile(request):

    mentor = get_object_or_404(
        Mentor,
        user=request.user
    )

    return render(
        request,
        "mentors/my_profile.html",
        {
            "mentor": mentor
        }
    )


# =====================================================
# EDIT MENTOR PROFILE
# =====================================================

@login_required
def edit_mentor_profile(request):

    mentor = get_object_or_404(
        Mentor,
        user=request.user
    )

    if request.method == "POST":

        form = MentorProfileForm(
            request.POST,
            request.FILES,
            instance=mentor
        )

        if form.is_valid():

            form.save()

            return redirect(
                "mentor_profile"
            )

    else:

        form = MentorProfileForm(
            instance=mentor
        )

    return render(
        request,
        "mentors/edit_profile.html",
        {
            "form": form,
            "mentor": mentor
        }
    )