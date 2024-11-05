# views/view.py
from utils.date_util import DateUtil
from utils.capturar_util import Capturar
import speech_recognition as sr
import threading
import queue
import ctypes

class View:
    
    def capturar_resposta(self):
        capturar = Capturar()
        resposta = capturar.capturar_resposta()
        self.exibir_resposta(resposta)
        return resposta

    def exibir_resposta(self, value):
        if value:
            print(f"Resposta: {value}")
        else:
            print("Resposta não disponível no momento.")

    def exibir_produtos(self, produtos):
        for produto in produtos.get("results", []):
            print(f"Produto: {produto['title']}, Preço: {produto['price']}, Link: {produto['permalink']}")

    def tratar_status(self, status):
        print(f"Status: {status}")

    def exibir_resposta_json(self, json_data):
        status = json_data.get('status')
        message = json_data.get('message')
        details = json_data.get('appointment_details', {})
        description = details.get('description')
        email = details.get('email')
        telefone = details.get('telefone')
        dateUtil = DateUtil()
        date_start = details.get('date_start')
        date_start = dateUtil.convert_date_format(date_start)
        date_end = details.get('date_end')
        date_end = dateUtil.convert_date_format(date_end)
        days = details.get('days')
        hour_checkin = details.get('hour_checkin')
        hour_checkout = details.get('hour_checkout')
        call_id = json_data.get('call_id')
        thread_id = json_data.get('thread_id')
        run_id = json_data.get('run_id')
        
        # Formatação estruturada
        formatted_response = f"""
        Mensagem: {message}

        Detalhes da Reserva:
        - Descrição: {description}
        - Email: {email}
        - Telefone: {telefone}
        - Data de Início: {date_start}
        - Data de Término: {date_end}
        - Dias Reservados: {days}
        - Check-in: {hour_checkin}
        - Check-out: {hour_checkout}
        
        Observação: A confirmação da reserva será feita mediante pagamento.
        """
        self.exibir_resposta(formatted_response)
