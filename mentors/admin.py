from django.contrib import admin

from .models import Mentor, Availability, SessionBooking

@admin.register(Mentor)
class MentorAdmin(admin.ModelAdmin):
    list_display = ("name", "expertise", "experience", "user")
    search_fields = ("name", "expertise")


@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = (
        "mentor",
        "date",
        "start_time",
        "end_time",
        "is_available",
    )

    list_filter = ("date", "is_available")

@admin.register(SessionBooking)
class SessionBookingAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "mentor",
        "availability",
        "topic",
        "status",
        "created_at",
    )

    list_filter = ("status", "mentor")
    search_fields = (
        "student__username",
        "mentor__name",
        "topic",
    )