from django.conf import settings
from django.views import View
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from django.http import HttpResponseRedirect
from django.urls import reverse
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from django.http import JsonResponse


class GoogleCalendarInitView(View):
    def get(self, request, *args, **kwargs):
        flow = Flow.from_client_config(
            settings.GOOGLE_OAUTH_CLIENT_CONFIG,
            scopes=settings.GOOGLE_OAUTH_SCOPES
        )
        flow.redirect_url = request.build_absolute_uri(reverse('google-calendar-redirect'))

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )

        request.session['google_auth_state'] = state

        return HttpResponseRedirect(authorization_url)


class GoogleCalendarRedirectView(View):
    def get(self, request, *args, **kwargs):
        state = request.GET.get('state')
        code = request.GET.get('code')

        if state != request.session.get('google_auth_state'):
            return JsonResponse({'error': 'Invalid state parameter.'}, status=401)

        flow = Flow.from_client_config(
            settings.GOOGLE_OAUTH_CLIENT_CONFIG,
            scopes=settings.GOOGLE_OAUTH_SCOPES,
            state=state
        )
        flow.redirect_uri = request.build_absolute_uri(reverse('google-calendar-redirect'))

        try:
            flow.fetch_token(code=code)
        except HttpError:
            return JsonResponse({'error': 'Failed to retrieve access token.'}, status=400)

        credentials = flow.credentials
        service = build('calendar', 'v3', credentials=credentials)

        events_result = service.events().list(calendarId='primary', timeMin='2023-04-23T00:00:00.000000Z',
                                              timeMax='2023-04-24T00:00:00.000000Z', maxResults=20, singleEvents=True,
                                              orderBy='startTime').execute()

        events = events_result.get('items', [])

        return JsonResponse({'events': events})
