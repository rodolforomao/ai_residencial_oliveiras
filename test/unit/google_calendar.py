import json
import unittest
from models.api_make_model import APIMakeModel
from config.config import API_KEY, API_URL, ID_ASSISTENT, WEBHOOK_MAKE_AGENDAMENTO

class UnitTestGoogleCalendar(unittest.TestCase):
    def setUp(self):
        self.api_make_model = APIMakeModel()
        
    def test_iniciar(self):
        data_str = '{"hotel": "Residencial Oliveiras", "dias_ocupados": [{"date_start": "2024-10-26", "date_end": "2024-10-28"}]}'
        data_json = json.loads(data_str)
        data_json["call_id"] = "cal_id123"
        data_json["thread_id"] = "thread_id123"
        data_json["run_id"] = "run_id123"
        data_json["Authorization"] = API_KEY
        response = self.api_make_model.webhook_agendamento(data_json)
        
        # You can add assertions to validate the response here
        self.assertIsNotNone(response)  # Example assertion
        # Add more assertions based on expected response
    
if __name__ == "__main__":
    unittest.main()
