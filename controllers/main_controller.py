# controllers/main_controller.py
import time
import json
from models.api_model import APIModel
from models.api_make_model import APIMakeModel
from models.mercado_pago_model import MercadoPagoModel
from models.google_calendar_model import GoogleCalendar
from models.date_util import DateUtil
from utils.requests_util import RequestsUtil
from utils.google_calendar_utils import GoogleCalendarUtil

from views.view import View

class MainController:
    def __init__(self):
        self.api_model = APIModel()
        self.api_mp_model = MercadoPagoModel()
        
        self.view = View()

    def iniciar(self):
        while True:
            pergunta = self.view.capturar_resposta()
            
            if not self.api_model.thread_id and not self.api_model.run_id:
                request_response = self.api_model.criar_run(pergunta)
            else:
                request_response = self.api_model.criar_mensagem(pergunta)
                if 'error' in request_response:
                    message = request_response['error'].get('message')
                    if message:
                        print(message)
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
                                self.date_util = DateUtil()
                                json_data = self.date_util.check_date(json_data)
                                # self.api_make_model = APIMakeModel(self.api_model.thread_id,self.api_model.run_id,self.api_model.run_status, self.api_model.call_id, self.api_model.arguments)
                                # self.api_make_model.webhook_consultar_disponibilidade(json_data)
                                
                                googlecalendarutil = GoogleCalendarUtil()
                                output_text = googlecalendarutil.check_available(json_data)
                                requests_util = RequestsUtil(self)
                                response_submit_tool_output = requests_util.request_submit_tool(output_text)
                                
                                if response_submit_tool_output:
                                    if response_submit_tool_output.status_code == 200:
                                        print('submit_tool_ouput: ok - cAgenda')
                                        #aguardando_recuperacao_mensagem = False
                                        #aguardando_resposta = False
                                
                        elif function_name == "Agendar":
                            if function_json:
                                json_data = json.loads(function_json)
                                self.api_make_model = APIMakeModel(self.api_model.thread_id,self.api_model.run_id,self.api_model.run_status, self.api_model.call_id, self.api_model.arguments)
                                self.date_util = DateUtil()
                                json_data = self.date_util.check_date_agendar(json_data)
                                #response = self.api_make_model.webhook_realizar_agendamento(json_data)
                                
                                googlecalendarutil = GoogleCalendarUtil()
                                output_text = googlecalendarutil.create_event(json_data)
                                requests_util = RequestsUtil(self)
                                response_submit_tool_output = requests_util.request_submit_tool(output_text)
                                
                                if output_text and response_submit_tool_output:
                                    if response_submit_tool_output.status_code == 200 and 'confirmed' in output_text.get('status'):
                                        #aguardando_recuperacao_mensagem = False
                                        #aguardando_resposta = False
                                        self.view.exibir_resposta_json(json_data)
                                        
                                        
                        elif function_name == "Pagamento":
                            if function_json:
                                json_data = json.loads(function_json)
                                #self.api_make_model = APIMakeModel(self.api_model.thread_id,self.api_model.run_id,self.api_model.run_status, self.api_model.call_id, self.api_model.arguments)
                                self.date_util = DateUtil()
                                json_data = self.date_util.check_date_agendar(json_data)
                                response = self.api_mp_model.generate_with_json(json_data)
                                if response:
                                    if 'approved' in response.text:
                                        aguardando_recuperacao_mensagem = False
                                        aguardando_resposta = False
                                        output_text = 'Link para pagamento:' + json.loads(response.text).get("init_point")
                                        requests_util = RequestsUtil(self)
                                        response_submit_tool_output = requests_util.request_submit_tool(output_text)
                                        
                        elif function_name == "cPagamento":
                            if function_json:
                                json_data = json.loads(function_json)
                                #self.api_make_model = APIMakeModel(self.api_model.thread_id,self.api_model.run_id,self.api_model.run_status, self.api_model.call_id, self.api_model.arguments)
                                self.date_util = DateUtil()
                                json_data = self.date_util.check_date_agendar(json_data)
                                response = self.api_mp_model.generate_with_json(json_data)
                                if response:
                                    if 'approved' in response.text:
                                        aguardando_recuperacao_mensagem = False
                                        aguardando_resposta = False
                                        output_text = 'Link para pagamento:' + json.loads(response.text).get("init_point")
                                        requests_util = RequestsUtil(self)
                                        response_submit_tool_output = requests_util.request_submit_tool(output_text)

                        else:
                            pass
                            
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
                        
