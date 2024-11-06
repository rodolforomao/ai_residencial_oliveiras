# utils/requests_util.py
import requests
import pytz
from config.config import API_KEY, API_URL, WEBHOOK_MAKE_AGENDAMENTO, WEBHOOK_MAKE_AGENDAR, CALENDAR_ID_GOOGLE

from google.oauth2 import service_account
from googleapiclient.discovery import build

from datetime import datetime, timedelta


class GoogleCalendarUtil:
    
    def __init__(self):
        SCOPES = [
        "https://www.googleapis.com/auth/calendar",
    ]
        self.credentials = service_account.Credentials.from_service_account_file(
            'files/google_calendar/credentials2.json', scopes=SCOPES
        )
        self.service = build('calendar', 'v3', credentials=self.credentials)
        
        self.calendar_id = CALENDAR_ID_GOOGLE

    def get_events(self, num_events=10):
        try:

            now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
            week_from_now = (datetime.utcnow() + timedelta(days=365)).isoformat() + 'Z'

            events_result = self.service.events().list(calendarId=self.calendar_id, timeMin=now, timeMax=week_from_now,
                                                maxResults=num_events, singleEvents=True,
                                                orderBy='startTime').execute()
            events = events_result.get('items', [])
            return events
        except Exception as e:
            print(f"An error occurred: {e}")
        return None

    def check_available(self, json_data):
        
        resposta = "A consulta não foi realizada, tente novamente mais tarde"
        text_reservados = ""
        
        if json_data and 'dias_ocupados' in json_data:
            dias_a_verificar = json_data['dias_ocupados']
            response = self.get_events()  # Obtém a lista de eventos

            if response:
                
                resposta = "Todos os apartamentos estão livres"
                apartamentos_ocupados = []

                for item in response:
                    start = item['start'].get('dateTime', item['start'].get('date'))
                    end = item['end'].get('dateTime', item['end'].get('date'))
                    start_time_ocuppied = datetime.strptime(start[:10], '%Y-%m-%d')  # Extrai somente a data
                    end_time_ocuppied = datetime.strptime(end[:10], '%Y-%m-%d')      # Extrai somente a data

                    summary = item.get('summary', '')
                    apartamento_numero = summary.split(" - ")[0] if " - " in summary else summary

                    for periodo in dias_a_verificar:
                        date_start_a_verificar = datetime.strptime(periodo['date_start'], '%Y-%m-%d')
                        date_end_a_verificar = datetime.strptime(periodo['date_end'], '%Y-%m-%d')

                        if (start_time_ocuppied <= date_end_a_verificar and end_time_ocuppied >= date_start_a_verificar):
                            apartamentos_ocupados.append({
                                'apartamento': apartamento_numero,
                                'date_start': start_time_ocuppied.strftime('%Y-%m-%d'),
                                'date_end': end_time_ocuppied.strftime('%Y-%m-%d')
                            })
                            text_reservados += f"O apartamento {apartamento_numero} está reservado entre os dias {start_time_ocuppied.strftime('%Y-%m-%d')} e {end_time_ocuppied.strftime('%Y-%m-%d')};"

                if apartamentos_ocupados:
                    return text_reservados
                
        return resposta
   

    def create_event(self, json_data):
        try:
            index1 = "appointment_details"
            index2 = "description"
            value_none = "Agendamento não identificado"
            summary = json_data.get(index1, {}).get(index2, value_none)
            index2 = "date_start"
            value_none = datetime.now() + timedelta(days=-1)
            date_start = json_data.get(index1, {}).get(index2, value_none)
            
            index2 = "hour_checkin"
            value_none = "14:00"
            hour_checkin = json_data.get(index1, {}).get(index2, value_none)
            
            index2 = "date_end"
            value_none = datetime.now() + timedelta(days=-1)
            date_end = json_data.get(index1, {}).get(index2, value_none)

            index2 = "hour_checkout"
            value_none = "11:00"
            hour_checkout = json_data.get(index1, {}).get(index2, value_none)
            
            timezone = 'America/Sao_Paulo'
            
            start_date = f"{date_start}T{hour_checkin}:00"  # Formato ISO: 'YYYY-MM-DDTHH:MM:SS'
            end_date = f"{date_end}T{hour_checkout}:00"
            
            start_date_dt = datetime.fromisoformat(start_date)
            end_date_dt = datetime.fromisoformat(end_date)
            
            # Verifica se as datas de início e fim foram fornecidas
            if not start_date or not end_date:
                raise ValueError("As datas de início e fim são obrigatórias.")
            
            index2 = "email"
            value_none = "rodolforomao@gmail.com"
            e_mail_guest = json_data.get(index1, {}).get(index2, value_none)
            

            # Define o fuso horário
            tz = pytz.timezone(timezone)
            start_datetime = tz.localize(datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S'))
            end_datetime = tz.localize(datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%S'))
            
            if end_datetime.date() == datetime(end_datetime.year, end_datetime.month, end_datetime.day).date() and end_datetime.hour < 12:
                end_datetime = (end_datetime - timedelta(days=1)).replace(hour=23, minute=59, second=59)
                pass

            # Example: Color ID 5 (change to any number 1-11)
            #  "colorId"
            #  Azul: 1
            #  Marrom: 6
            #  Amarelo: 5
            # Configura os detalhes do evento
            color_map = {
                "apartamento 1": "8",  # Brown color ID
                "apartamento 2": "5",  # Yellow color ID
                "apartamento 3": "1"   # Blue color ID
            }
            # Determine the colorId based on summary content
            color_id = None
            if "apartamento 1" in summary.lower():
                color_id = color_map["apartamento 1"]
            elif "apartamento 2" in summary.lower():
                color_id = color_map["apartamento 2"]
            elif "apartamento 3" in summary.lower():
                color_id = color_map["apartamento 3"]
            
            event = {
                'summary': '🤖' + summary.replace('🤖',''),
                'location': "Residencial Oliveiras - Brasília - Vila Planalto",
                'description': "",
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': timezone,
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': timezone,
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 1440},  # 1 dia antes
                        {'method': 'email', 'minutes': 2880},  # 2 dias antes
                        {'method': 'popup', 'minutes': 10080}, # 7 dias antes
                    ],
                },
                "colorId": color_id
                # , "attendees": [
                #     {"email": e_mail_guest}
                # ],
            }

            # Cria o evento no Google Calendar
            event_result = self.service.events().insert(calendarId=self.calendar_id, body=event).execute()

            print(f"Evento criado: {event_result.get('htmlLink')}")
            return event_result
        except Exception as e:
            print(f"Ocorreu um erro ao criar o evento: {e}")
            return None