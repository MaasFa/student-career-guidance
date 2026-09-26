from django.urls import path
from . import views


urlpatterns = [

    path(
        "create/",
        views.create_query,
        name="create_query"
    ),
    path(
        "mentor-queries/",
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
        "edit/<int:session_id>/",
        views.edit_session,
        name="edit_session"
    ),
    path(
        "cancel/<int:session_id>/",
        views.cancel_session,
        name="cancel_session"
    ),

]