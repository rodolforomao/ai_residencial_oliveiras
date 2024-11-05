# utils/requests_uril.py
import requests
from config.config import API_KEY, API_URL, ID_ASSISTENT, WEBHOOK_MAKE_AGENDAMENTO, WEBHOOK_MAKE_AGENDAR

class RequestsUtil:
    
    TYPE_RESPONSE_GOOGLE_CALENDAR = 1
    
    def __init__(self, parameters):
        self.thread_id = parameters.api_model.thread_id
        self.run_id = parameters.api_model.run_id
        self.run_status = parameters.api_model.run_status
        self.call_id = parameters.api_model.call_id
        self.arguments = parameters.api_model.arguments

    def request_submit_tool(self, output_text, type_operation = 1):
        url = self.get_url_submit_tools_output()
        headers = self.get_headers_autorization()
        
        if type(output_text) != type('') and output_text:
            if type_operation  == self.TYPE_RESPONSE_GOOGLE_CALENDAR:
                output_text = "O status da reserva é: " + output_text.get('status')
        data = self.get_body_submit_tools_output(output_text)
        response = requests.post(url, headers=headers, json=data)
        return response
        
    def get_headers_autorization(self):
        return {
            "Authorization": f"Bearer {API_KEY}",
            "OpenAI-Beta": "assistants=v2"
        }
    
    def get_url_submit_tools_output(self):
        return f'{API_URL}/{self.thread_id}/runs/{self.run_id}/submit_tool_outputs'
    
    def get_body_submit_tools_output(self, output_text):
        return {
                    "tool_outputs": [
                        {
                            "tool_call_id": self.call_id,
                            "output": output_text
                        }
                    ]
                }