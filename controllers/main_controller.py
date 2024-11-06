# controllers/main_controller.py
import time
import json
import types
from models.api_model import APIModel
from models.api_make_model import APIMakeModel
from models.mercado_pago_model import MercadoPagoModel
from models.google_calendar_model import GoogleCalendar
from models.date_util import DateUtil
# from utils.management_request_status_util import ManagementRequestsSatus
from utils.requests_util import RequestsUtil
from utils.google_calendar_utils import GoogleCalendarUtil

from views.view import View

class MainController:
    def __init__(self):
        self.api_model = APIModel()
        self.api_mp_model = MercadoPagoModel()
        
        self.view = View()
        self.schedule_sent_status = []

    def iniciar(self, msg = None, answer_loop = True, assistent_id = None, run_id = None, thread_id = None):
        if run_id is not None and run_id:
            self.api_model.run_id = run_id
        if thread_id is not None and thread_id:
            self.api_model.thread_id = thread_id
        resposta = None
        while True:
            output_text = None
            if msg is None:
                msg = self.view.capturar_resposta()
            elif isinstance(msg, dict):
                pergunta = msg['message']
            
            if not self.api_model.thread_id and not self.api_model.run_id:
                request_response = self.api_model.criar_run(pergunta, assistent_id)
            else:
                request_response = self.api_model.criar_mensagem(pergunta)
                if 'error' in request_response:
                    message = request_response['error'].get('message')
                    if message:
                        print(message)
                self.api_model.manter_run(assistent_id)

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
                        qnt_requires_actions = self.api_model.get_qnty_actions(retrive_response)
                        calls_ids = []
                        output_responses = []
                        for index in range(qnt_requires_actions):
                            function_name = self.api_model.get_function_properties(retrive_response,'name', index)
                            function_json = self.api_model.get_function_properties(retrive_response,'arguments', index)
                            function_call_id = self.api_model.get_function_properties(retrive_response,'id', index, call_id = True)
                            calls_ids.append(function_call_id)
                            if function_name == "cAgenda":
                                if function_json:
                                    json_data = json.loads(function_json)
                                    self.date_util = DateUtil()
                                    json_data = self.date_util.check_date(json_data)
                                    
                                    googlecalendarutil = GoogleCalendarUtil()
                                    output_text = googlecalendarutil.check_available(json_data)
                                    #requests_util = RequestsUtil(self, function_call_id)
                                    #response_submit_tool_output = requests_util.request_submit_tool(output_text)
                                    output_responses.append(output_text)
                                    
                                    # if response_submit_tool_output:
                                    #     if response_submit_tool_output.status_code == 200:
                                    #         print('submit_tool_ouput: ok - cAgenda')
                                    
                            elif function_name == "Agendar":
                                if function_json:
                                    json_data = json.loads(function_json)
                                    self.api_make_model = APIMakeModel(self.api_model.thread_id,self.api_model.run_id,self.api_model.run_status, self.api_model.call_id, self.api_model.arguments)
                                    self.date_util = DateUtil()
                                    json_data = self.date_util.check_date_agendar(json_data)
                                    
                                    googlecalendarutil = GoogleCalendarUtil()
                                    # managementRequests = ManagementRequestsSatus(self.schedule_sent_status)
                                    
                                    # has_sent_schedule, has_sent_submit_output = managementRequests.has_sent_successfully(json_data)
                                    
                                    # if  has_sent_schedule is False:
                                    output_text = googlecalendarutil.create_event(json_data)
                                    if 'confirmed' in output_text.get('status'):
                                        # managementRequests.add_update_or_status_code(json_data, None, output_text.get('status'))
                                        output_responses.append('Agendamento realizado com sucesso:' + output_text.get('status'))
                                    else:
                                        output_responses.append('Reversa não emitida, estamos enfrentando problemas em nossos sistema')
                                        
                                    response_submit_tool_output = None
                                    #requests_util = RequestsUtil(self)
                                    # if has_sent_submit_output is False:
                                    #     response_submit_tool_output = requests_util.request_submit_tool(output_text)
                                    # managementRequests.add_update_or_status_code(json_data, response_submit_tool_output.status_code)
                                    # has_sent_submit_output, has_sent_schedule  = managementRequests.has_sent_successfully(json_data)
                                    
                                    # if has_sent_schedule and has_sent_submit_output:
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
                                            output_responses.append(output_text)
                                        else:
                                            output_responses.append("Não foi possível gerar link de pagamento, tente novamente mais tarde. (error 1)")
                                    else:
                                        output_responses.append("Não foi possível gerar link de pagamento, tente novamente mais tarde. (error 1)")
                                            
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
                                            resposta = output_text
                            else:
                                pass
                                
                            self.view.tratar_status(run_status)

                        if calls_ids and output_responses:
                            requests_util = RequestsUtil(self)
                            response_submit_tool_output = requests_util.request_submit_tool(output_responses, calls_ids)
                            
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
                        
            if answer_loop is False:
                if resposta is None:
                    resposta = output_text
                if resposta:
                    return resposta,self.api_model.run_id, self.api_model.thread_id
                return None

    