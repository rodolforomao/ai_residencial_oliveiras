# models/api_model.py
import requests
from config.config import API_KEY, API_URL, ID_ASSISTENT


class APIModel:
    def __init__(self, thread_id=None, run_id=None, run_status=None, call_id=None, arguments=None):
        self.thread_id = thread_id
        self.run_id = run_id
        self.run_status = run_status
        self.call_id = call_id
        self.arguments = arguments

    def get_headers(self):
        return {
            "Authorization": f"Bearer {API_KEY}",
            "OpenAI-Beta": "assistants=v2"
        }

    def criar_mensagem(self, pergunta):
        url = f"{API_URL}/{self.thread_id}/messages"
        headers = self.get_headers()
        data = {
            "role": "user",
            "content": pergunta
        }
        response = requests.post(url, headers=headers, json=data)
        return response.json()

    def obter_mensagem(self):
        url = f"{API_URL}/{self.thread_id}/messages"
        headers = self.get_headers()
        response = requests.get(url, headers=headers)
        return self.get_response(response.json())

    def obter_status_run_retrieve(self):
        url = f"{API_URL}/{self.thread_id}/runs/{self.run_id}"
        headers = self.get_headers()
        response = requests.get(url, headers=headers)
        response = response.json()
        if response:
            self.run_status = response.get('status')
            self.call_id = self.get_call_id(response)
            self.arguments = self.get_function_arguments(response)
        else:
            pass
        return response

    def criar_run(self, pergunta, assistent_id = None):
        if assistent_id is None:
            assistent_id = ID_ASSISTENT
        url = f"{API_URL}/runs"
        headers = self.get_headers()
        data = {
            "assistant_id": assistent_id,
            "thread": {
                "messages": [
                    {"role": "user", "content": pergunta}
                ]
            }
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            self.run_id = result.get("id")
            self.thread_id = result.get("thread_id")
        else:
            print('Status code: ' + str(response.status_code))
            print('Erro: ' + response.text)
        return response

    def manter_run(self, assistent_id = None):
        if assistent_id is None:
            assistent_id = ID_ASSISTENT
        url = f"{API_URL}/{self.thread_id}/runs"
        headers = self.get_headers()
        data = {"assistant_id": assistent_id}
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            self.run_id = result.get("id")
        return response

    def get_call_id(self, status_response):
        # Call id: data.required_action.submit_tool_outputs.tool_calls[0].id
        return (
            status_response.get('required_action') and
            status_response['required_action'].get('submit_tool_outputs') and
            status_response['required_action']['submit_tool_outputs'].get('tool_calls') and
            len(status_response['required_action']['submit_tool_outputs']['tool_calls']) > 0 and
            status_response['required_action']['submit_tool_outputs']['tool_calls'][0].get(
                'id')
        )

    def get_function_arguments(self, status_response):
        # Arguments: data.required_action.submit_tool_outputs.tool_calls[0].function.arguments
        return (
            status_response.get('required_action') and
            status_response['required_action'].get('submit_tool_outputs') and
            status_response['required_action']['submit_tool_outputs'].get('tool_calls') and
            len(status_response['required_action']['submit_tool_outputs']['tool_calls']) > 0 and
            status_response['required_action']['submit_tool_outputs']['tool_calls'][0].get('function') and
            status_response['required_action']['submit_tool_outputs']['tool_calls'][0]['function'].get(
                'arguments')
        )

    def get_response(self, resposta):
        return (
            resposta.get("data") and
            resposta["data"][0].get("content") and
            resposta["data"][0]["content"][0].get("text") and
            resposta["data"][0]["content"][0]["text"].get("value")
        )

    def get_function_properties(self, status_response, key, index = 0, call_id = False):
        required_action = status_response.get('required_action', {})
        submit_tool_outputs = required_action.get('submit_tool_outputs', {})
        tool_calls = submit_tool_outputs.get('tool_calls', [])

        # Verificar se a lista 'tool_calls' não está vazia e se o primeiro item contém 'function' e 'name'
        if index >= 0:
            if call_id:
                return tool_calls[index][key]
            elif tool_calls and 'function' in tool_calls[index] and 'name' in tool_calls[index]['function']:
                return tool_calls[index]['function'][key]

        # Retornar um valor padrão (por exemplo, None) caso algo esteja faltando
        return None

    def get_qnty_actions(self, status_response):
        required_action = status_response.get('required_action', {})
        submit_tool_outputs = required_action.get('submit_tool_outputs', {})
        tool_calls = submit_tool_outputs.get('tool_calls', [])

        # Verificar se a lista 'tool_calls' não está vazia e se o primeiro item contém 'function' e 'name'
        return len(tool_calls)
