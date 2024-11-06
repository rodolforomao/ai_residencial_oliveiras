# utils/requests_uril.py
import requests
from config.config import API_KEY, API_URL, WEBHOOK_MAKE_AGENDAMENTO, WEBHOOK_MAKE_AGENDAR

class RequestsUtil:
    
    TYPE_RESPONSE_GOOGLE_CALENDAR = 1
    
    def __init__(self, parameters):
        self.thread_id = parameters.api_model.thread_id
        self.run_id = parameters.api_model.run_id
        #self.run_status = parameters.api_model.run_status
        
        #self.arguments = parameters.api_model.arguments

    def request_submit_tool(self, body, call_ids):
        url = self.get_url_submit_tools_output()
        headers = self.get_headers_autorization()
        
        if body and call_ids:
            data = self.get_body_submit_tools_output(body, call_ids)
            response = requests.post(url, headers=headers, json=data)
            return response
        return None
        
    def get_headers_autorization(self):
        return {
            "Authorization": f"Bearer {API_KEY}",
            "OpenAI-Beta": "assistants=v2"
        }
    
    def get_url_submit_tools_output(self):
        return f'{API_URL}/{self.thread_id}/runs/{self.run_id}/submit_tool_outputs'
    
    def get_body_submit_tools_output(self, outputs, call_ids):
        return {
            "tool_outputs": [{"tool_call_id": call_id, "output": output} for call_id, output in zip(call_ids, outputs)]
        }