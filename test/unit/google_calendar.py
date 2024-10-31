import json
import unittest
from datetime import datetime, timedelta
from models.api_make_model import APIMakeModel
from config.config import API_KEY, API_URL, ID_ASSISTENT, WEBHOOK_MAKE_AGENDAMENTO

class UnitTestGoogleCalendar(unittest.TestCase):
    def setUp(self):
        self.api_make_model = APIMakeModel()

    def test_consultar_eventos(self):
        data_str = '{"hotel": "Residencial Oliveiras", "dias_ocupados": [{"date_start": "2024-10-26", "date_end": "2024-10-28"}]}'
        data_json = json.loads(data_str)
        data_json["call_id"] = "cal_id123"
        data_json["thread_id"] = "thread_id123"
        data_json["run_id"] = "run_id123"
        data_json["Authorization"] = API_KEY
        response = self.api_make_model.webhook_agendamento(data_json)

        self.assertIsNotNone(response)
        self.assertEqual(str(response.status_code), "200" | "400")
        self.assertIn("OK", response.reason)

    def test_criar_evento(self):
        
        start_date = datetime.now() + timedelta(days=3)
        end_date = start_date + timedelta(days=2)

        start_date_str = start_date.strftime('%Y-%m-%dT%H:%M:%S-03:00')
        end_date_str = end_date.strftime('%Y-%m-%dT%H:%M:%S-03:00')
        
        hospede = "Rodolfo Romão"
        qntHospede = str(3)
        valor = str(520.70)
        fonte = "Booking"
        
        emailHospede = "engenheirorodolforomao@gmail.com"
        
        # "colorId"
        # Azul: 1
        # Marrom: 6
        # Amarelo: 5
        event_data_str = f'''
        {{
            "summary": "🤖 Apartamento 4 - {qntHospede} hospede(s) - {hospede} - {fonte} - R${valor}/dia",
            "location": "Residencial Oliveiras",
            "description": "Locação do apartamento",
            "start": {{
                "dateTime": "{start_date_str}",
                "timeZone": "America/Sao_Paulo"
            }},
            "end": {{
                "dateTime": "{end_date_str}",
                "timeZone": "America/Sao_Paulo"
            }},
            "attendees": [
                {{ "email": "{emailHospede}" }}
            ],
            "colorId": "1"  
        }}
        '''
        
        event_data_json = json.loads(event_data_str)
        event_data_json["Authorization"] = API_KEY
        event_data_json["call_id"] = "cal_event_id123"
        
        # Simula a criação do evento via API
        response = self.api_make_model.webhook_locacao(event_data_json)

        # Asserções para validar se o evento foi criado com sucesso
        self.assertIsNotNone(response)
        self.assertEqual(str(response.status_code), "200")  # Exemplo de asserção baseada em resposta esperada
        self.assertIn("OK", response.reason)  # Verifica se o ID do evento foi retornado


if __name__ == "__main__":
    unittest.main()
