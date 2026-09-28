from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib.auth.decorators import login_required

from mentors.models import Mentor

from .forms import StudentQueryForm, SessionScheduleForm
from .models import StudentQuery, Session

@login_required
def create_query(request):

    if request.method == "POST":

        form = StudentQueryForm(request.POST)

        if form.is_valid():

            student_query = form.save(
                commit=False
            )

            student_query.student = request.user

            student_query.save()

            return redirect("dashboard")

    else:
        form = StudentQueryForm()

    return render(
        request,
        "queries/create_query.html",
        {
            "form": form
        }
    )
from mentors.models import Mentor
from .models import StudentQuery


@login_required
def mentor_queries(request):

    mentor = Mentor.objects.get(
        user=request.user
    )

    queries = StudentQuery.objects.filter(
        status="open"
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "queries/mentor_queries.html",
        {
            "mentor": mentor,
            "queries": queries,
        }
    )
@login_required
@login_required
def offer_session(request, query_id):

    mentor = Mentor.objects.get(
        user=request.user
    )

    student_query = get_object_or_404(
        StudentQuery,
        id=query_id,
        status="open"
    )

    session = Session.objects.create(
        student_query=student_query,
        student=student_query.student,
        mentor=mentor,
        status="offered"
    )

    student_query.status = "accepted"
    student_query.save()

    return redirect(
        "schedule_session",
        session_id=session.id
    )
@login_required
def schedule_session(request, session_id):

    mentor = Mentor.objects.get(
        user=request.user
    )

    session = get_object_or_404(
        Session,
        id=session_id,
        mentor=mentor,
        status="offered"
    )

    if request.method == "POST":

        form = SessionScheduleForm(
            request.POST,
            instance=session
        )

        if form.is_valid():

            session = form.save(
                commit=False
            )

            session.status = "confirmed"

            session.save()

            student_query = session.student_query
            student_query.status = "scheduled"
            student_query.save()

            return redirect("mentor_queries")

    else:

        form = SessionScheduleForm(
            instance=session
        )

    return render(
        request,
        "queries/schedule_session.html",
        {
            "session": session,
            "form": form,
        }
    )
@login_required
def edit_session(request, session_id):

    mentor = Mentor.objects.get(
        user=request.user
    )

    session = get_object_or_404(
        Session,
        id=session_id,
        mentor=mentor
    )

    if request.method == "POST":

        form = SessionScheduleForm(
            request.POST,
            instance=session
        )

        if form.is_valid():

            session = form.save(
                commit=False
            )

            session.status = "confirmed"
            session.save()

            return redirect("mentor_queries")

    else:

        form = SessionScheduleForm(
            instance=session
        )

    return render(
        request,
        "queries/edit_session.html",
        {
            "session": session,
            "form": form,
        }
    )


@login_required
def cancel_session(request, session_id):

    mentor = Mentor.objects.get(
        user=request.user
    )

    session = get_object_or_404(
        Session,
        id=session_id,
        mentor=mentor
    )

    if request.method == "POST":

        session.status = "cancelled"
        session.save()

        student_query = session.student_query
        student_query.status = "closed"
        student_query.save()

        return redirect("mentor_queries")

    return render(
        request,
        "queries/cancel_session.html",
        {
            "session": session,
        }
    )

@login_required
def my_queries(request):

    queries = StudentQuery.objects.filter(
        student=request.user
    ).order_by("-created_at")

    total_queries = queries.count()

    open_queries = queries.filter(
        status="open"
    ).count()

    scheduled_queries = queries.filter(
        status="scheduled"
    ).count()

    return render(
        request,
        "queries/my_queries.html",
        {
            "queries": queries,
            "total_queries": total_queries,
            "open_queries": open_queries,
            "scheduled_queries": scheduled_queries,
        }
    )
@login_required
def my_sessions(request):

    sessions = Session.objects.filter(
        student=request.user
    ).select_related(
        "mentor",
        "student_query"
    ).order_by(
        "date",
        "start_time"
    )

    return render(
        request,
        "queries/my_sessions.html",
        {
            "sessions": sessions
        }
    )