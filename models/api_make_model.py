# models/api_model.py
import requests
from config.config import API_KEY, API_URL, WEBHOOK_MAKE_AGENDAMENTO, WEBHOOK_MAKE_AGENDAR

class APIMakeModel:
    def __init__(self, thread_id=None, run_id=None, run_status=None, call_id=None, arguments=None):
        self.thread_id = thread_id
        self.run_id = run_id
        self.run_status = run_status
        self.call_id = call_id
        self.arguments = arguments

    def get_headers_simple(self):
        return {
            "Content-Type": "application/json",
        }
        
    def get_headers_autorization(self):
        return {
            "Authorization": f"Bearer {API_KEY}",
            "OpenAI-Beta": "assistants=v2"
        }

    def webhook_consultar_disponibilidade(self, json):
        url = f"{WEBHOOK_MAKE_AGENDAMENTO}"
        headers = self.get_headers_simple()
        json = self.webhook_add_submit_output(json)
        data = json
        response = requests.post(url, headers=headers, json=data)
        return response

    def webhook_realizar_agendamento(self, json):
        url = f"{WEBHOOK_MAKE_AGENDAR}"
        headers = self.get_headers_simple()
        json = self.webhook_add_submit_output(json)
        data = json
        response = requests.post(url, headers=headers, json=data)
        return response

    def webhook_add_submit_output(self, data_json):
        data_json["call_id"] = self.call_id
        data_json["thread_id"] = self.thread_id
        data_json["run_id"] = self.run_id
        data_json["Authorization"] = API_KEY
        return data_json