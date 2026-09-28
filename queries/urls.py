from django.urls import path
from . import views

from django.urls import path
from . import views


urlpatterns = [

    # Student
    path(
        "create/",
        views.create_query,
        name="create_query"
    ),

    path(
        "my-queries/",
        views.my_queries,
        name="my_queries"
    ),

    # Mentor
    path(
        "mentor/",
        views.mentor_queries,
        name="mentor_queries"
    ),

    path(
        "offer/<int:query_id>/",
        views.offer_session,
        name="offer_session"
    ),

    path(
        "schedule/<int:session_id>/",
        views.schedule_session,
        name="schedule_session"
    ),

    path(
        "edit-session/<int:session_id>/",
        views.edit_session,
        name="edit_session"
    ),

    path(
        "cancel-session/<int:session_id>/",
        views.cancel_session,
        name="cancel_session"
    ),
    path(
    "my-sessions/",
    views.my_sessions,
    name="my_sessions"
    ),
]