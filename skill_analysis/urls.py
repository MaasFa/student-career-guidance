from django.urls import path
from . import views

app_name = "skill_analysis"

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    path("create/", views.create_analysis_view, name="create_analysis"),
    path("<int:analysis_id>/", views.analysis_detail_view, name="analysis_detail"),
    path("<int:analysis_id>/delete/", views.delete_analysis_view, name="delete_analysis"),
    path("<int:analysis_id>/chat/", views.chat_assistant_view, name="chat_assistant"),
    path("item/<int:item_id>/status/", views.update_roadmap_item_status, name="update_roadmap_item_status"),
]
