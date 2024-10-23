# controllers/main_controller.py
import time
import json
from models.api_model import APIModel
from models.api_make_model import APIMakeModel
from views.view import View

class MainController:
    def __init__(self):
        self.api_model = APIModel()
        
        self.view = View()

    def iniciar(self):
        while True:
            pergunta = self.view.capturar_resposta("Digite sua pergunta: ")
            
            if not self.api_model.thread_id and not self.api_model.run_id:
                response = self.api_model.criar_run()
                
                #response = self.api_model.criar_run()
            else:
                self.api_model.criar_mensagem(pergunta)
                self.api_model.manter_run()

            aguardando_resposta = True
            toggleMsg = True
            
            while aguardando_resposta:
                time.sleep(0.5)
                retrive_response = self.api_model.obter_status_run_retrieve()
                if retrive_response:
                    run_status = retrive_response.get('status')
                    if run_status == "completed":
                        aguardando_recuperacao_mensagem = True
                        while aguardando_recuperacao_mensagem:
                            time.sleep(0.5)
                            resposta = self.api_model.obter_mensagem()
                            if resposta != pergunta:
                                self.view.exibir_resposta(resposta)
                                aguardando_recuperacao_mensagem = False
                                aguardando_resposta = False
                            else:
                                print('Aguardando resposta')
                    if run_status == "required_action":
                        function_name = self.api_model.get_function_properties(retrive_response)
                        self.view.tratar_status(run_status)
                    if run_status == "requires_action":
                        function_name = self.api_model.get_function_properties(retrive_response,'name')
                        function_json = self.api_model.get_function_properties(retrive_response,'arguments')
                        if function_name == "cAgenda":
                            if function_json:
                                json_data = json.loads(function_json)
                                self.api_make_model = APIMakeModel(self.api_model.thread_id,self.api_model.run_id,self.api_model.run_status, self.api_model.call_id, self.api_model.arguments)
                                self.api_make_model.webhook_agendamento(json_data)
                        self.view.tratar_status(run_status)
                    if run_status == "in_progress":
                        if toggleMsg:
                            self.view.tratar_status(run_status)
                        toggleMsg = not toggleMsg
                    if run_status == "failed":
                        aguardando_recuperacao_mensagem = False
                        aguardando_resposta = False
                        self.view.exibir_resposta(retrive_response.get('error'))
                        print('Tente novamente mais tarde.')
                    else:
                        self.view.tratar_status(run_status)
                        
