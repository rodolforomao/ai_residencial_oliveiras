import time
import threading

from config.config import API_KEY, API_URL, ID_ASSISTENT

# Foreignt classes
import sys

from controllers.main_controller import MainController
sys.path.append(r'C:\desenvolvimento\Estudos\IA\integracao_via_web\gpt_whats_chabot')
from application.model.whatsapp import Whatsapp
from application.model.queue_manager import QueueManager

class PrincipalController:
    
    def __init__(self):
        print(f'Class: {self.__class__.__name__} - constructor')
        self.queue_manager = QueueManager()
        self.thread_ler = None
        self.thread_processar = None
        self.thread_enviar = None
        self.user_contexts = {}

    def executar(self):
        while True:
            try:
                # Iniciar threads
                # Verifica se a thread de ler mensagens está ativa
                if self.thread_ler is None or not self.thread_ler.is_alive():
                    print('Iniciando thread para ler mensagens...')
                    self.thread_ler = threading.Thread(target=self.ler_mensagens, daemon=True)
                    self.thread_ler.start()

                # Verifica se a thread de processar perguntas está ativa
                if self.thread_processar is None or not self.thread_processar.is_alive():
                    print('Iniciando thread para processar perguntas...')
                    self.thread_processar = threading.Thread(target=self.processar_perguntas, daemon=True)
                    self.thread_processar.start()

                # Verifica se a thread de enviar mensagens está ativa
                if self.thread_enviar is None or not self.thread_enviar.is_alive():
                    print('Iniciando thread para enviar mensagens...')
                    self.thread_enviar = threading.Thread(target=self.enviar_mensagens, daemon=True)
                    self.thread_enviar.start()

                while self.thread_enviar.is_alive() and self.thread_processar.is_alive() and self.thread_ler.is_alive():
                    time.sleep(1)
            except Exception as e: 
                print(f'exception: {e}')
            print('while')
            
        
    def display_users(self):
        users = self.model.get_all_users()
        self.view.show_users(users)

    # Criar uma thread para ler mensagens
    def ler_mensagens(self):
        whatsapp = Whatsapp()
        while True:
            time.sleep(1)
            whatsapp_driver, whatsapp_perguntas = whatsapp.lerMensagensWhatsapp()
            if whatsapp_perguntas is not None:
                for pergunta in whatsapp_perguntas:
                    self.queue_manager.adicionar_pergunta(pergunta)
                    self.queue_manager.adicionar_pergunta_respondida([pergunta])
                
                whatsapp.refresh_webdriver()

    # Criar uma thread para processar perguntas
    def processar_perguntas(self):
        aiagent = MainController()
        while True:
            time.sleep(1)
            if self.queue_manager.perguntas and len(self.queue_manager.perguntas):
                pergunta = self.queue_manager.processar_perguntas()
                for each_msg in pergunta: 
                    if each_msg:
                        #user_context = self.user_contexts.get(user_id, {})
                        user_id_number = each_msg.get('number')
                        self.user_context = self.user_contexts.get(user_id_number, {})

                        #aiagent_respostas, run_id, thread_id = aiagent.iniciar(each_msg, answer_loop = False, assistent_id = ID_ASSISTENT, run_id=self.user_context.get("run_id"), thread_id = self.user_context.get("thread_id"))
                        aiagent_respostas, run_id, thread_id = aiagent.iniciar(each_msg, answer_loop = False, assistent_id = ID_ASSISTENT)
                        self.queue_manager.adicionar_resposta(aiagent_respostas)
                        
                        self.user_contexts[user_id_number] = {
                            "run_id": run_id,
                            "thread_id": thread_id,
                        }

    # Criar uma thread para enviar mensagens
    def enviar_mensagens(self):
        whatsapp = Whatsapp()
        while True:
            time.sleep(1)
            if self.queue_manager.respostas and len(self.queue_manager.respostas) and self.queue_manager.perguntas_respondidas and len(self.queue_manager.perguntas_respondidas):
                resposta = self.queue_manager.respostas.pop(0)
                pergunta = self.queue_manager.perguntas_respondidas.pop(0)
                print('Responda pelo whatsapp')
                # whatsapp.enviarMensagensWhatsapp(whatsapp_driver, whatsapp_perguntas, aiagent_respostas)
                whatsapp.enviarMensagensWhatsapp(pergunta, resposta)
                
                whatsapp.refresh_webdriver()
                