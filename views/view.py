# views/view.py
from utils.date_util import DateUtil
import speech_recognition as sr

class View:
    
    def capturar_resposta(self):
            # Perguntar se o usuário deseja usar voz
        escolha = input("Deseja fazer a pergunta por áudio? (s/n): ")
        if escolha.lower() == 's':
            return self.capturar_audio()
        else:
            pergunta = ""
            return input(pergunta)

    def capturar_audio(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Aguardando a pergunta...")
            audio = recognizer.listen(source)

        try:
            resposta = recognizer.recognize_google(audio, language='pt-BR')  # Use o idioma desejado
            print(f"Você perguntou: {resposta}")
            return resposta
        except sr.UnknownValueError:
            print("Não consegui entender o áudio.")
            return ""
        except sr.RequestError as e:
            print(f"Erro ao se comunicar com o serviço de reconhecimento: {e}")
            return ""

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
        # formatted_response = f"""
        # Status: {status.capitalize()}
        
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
        # Identificadores:
        # - Call ID: {call_id}
        # - Thread ID: {thread_id}
        # - Run ID: {run_id}
        # """
        self.exibir_resposta(formatted_response)
        #print(formatted_response)