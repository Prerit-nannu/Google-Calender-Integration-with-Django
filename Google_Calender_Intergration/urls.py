from django.urls import path
from .views import GoogleCalendarInitView, GoogleCalendarRedirectView

urlpatterns = [
    path('calendar/init/', GoogleCalendarInitView.as_view(), name='google-calendar-init'),
    path('calendar/redirect/', GoogleCalendarRedirectView.as_view(), name='google-calendar-redirect'),
]

