from django.urls import path
from . import views


urlpatterns = [

    path(
        "dashboard/",
        views.mentor_dashboard,
        name="mentor_dashboard"
    ),

    path(
        "availability/add/",
        views.add_availability,
        name="add_availability"
    ),

    path(
        "list/",
        views.mentor_list,
        name="mentor_list"
    ),
    path(
        "detail/<int:mentor_id>/",
        views.mentor_detail,
        name="mentor_detail"
    ),
    path(
        "profile/edit/",
        views.edit_mentor_profile,
        name="edit_mentor_profile"
    ),
    path(
        "profile/",
        views.mentor_profile,
        name="mentor_profile"
    ),
]