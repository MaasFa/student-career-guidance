from django.urls import path
from . import views


urlpatterns = [

    path(
        "create/",
        views.create_workshop,
        name="create_workshop"
    ),

    path(
        "list/",
        views.workshop_list,
        name="workshop_list"
    ),

]