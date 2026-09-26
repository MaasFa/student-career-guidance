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
]