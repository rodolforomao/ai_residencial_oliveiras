# models/google_calendar_model.py
import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from config.config import GOOGLE_CONSOLE_CREDENTIALS_API_FILE

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

class GoogleCalendar:
    def __init__(self):
        pass
    
    def check_date(self):
        """Mostra os próximos 10 eventos do calendário."""
        creds = None

        if os.path.exists('token.pickle'):
            with open(pickle, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    GOOGLE_CONSOLE_CREDENTIALS_API_FILE, SCOPES)
                creds = flow.run_local_server(port=8080)
            # Salve as credenciais para a próxima execução
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('calendar', 'v3', credentials=creds)

        # Chame a API do Google Calendar
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indica UTC
        print('Obtendo os próximos 10 eventos')
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                            maxResults=10, singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('Nenhum evento encontrado.')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
    
    
    