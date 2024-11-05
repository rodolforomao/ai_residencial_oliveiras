# capturar_util

from utils.date_util import DateUtil
import speech_recognition as sr
import threading
import queue
import ctypes

class Capturar:
    
    def matar_thread(self, thread):
        if not thread.is_alive():
            print("Thread já finalizada.")
            return
        thread_id = thread.ident
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread_id), ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread_id), 0)
            print("Erro ao finalizar a thread.")
        else:
            print("Thread finalizada.")
    
    def capturar_resposta(self):
        """
        Captura simultaneamente áudio e texto do usuário.
        Se um áudio válido for detectado, ele terá prioridade sobre o texto digitado.
        """
        resposta_queue = queue.Queue()  # Fila para armazenar respostas de áudio e texto
        timeout_event = threading.Event()

        def capturar_audio():
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                print("Você pode falar ou digitar sua pergunta...")
                try:
                    audio = recognizer.listen(source, timeout=5)  # Escuta por 5 segundos
                    resposta_audio = recognizer.recognize_google(audio, language='pt-BR')
                    if resposta_audio.strip():  # Adiciona à fila apenas se houver conteúdo significativo
                        resposta_queue.put(("audio", resposta_audio))
                        timeout_event.set()  # Indica que uma resposta foi obtida
                except (sr.UnknownValueError, sr.RequestError):
                    # Caso de erro ou ruído no áudio, ignorar a entrada de áudio
                    pass

        def capturar_texto():
            resposta_texto = input("Digite sua pergunta: ")
            if resposta_texto.strip():  # Adiciona à fila apenas se houver conteúdo significativo
                resposta_queue.put(("texto", resposta_texto))
                timeout_event.set()  # Indica que uma resposta foi obtida

        # Inicia threads para captura de áudio e texto simultaneamente
        audio_thread = threading.Thread(target=capturar_audio)
        texto_thread = threading.Thread(target=capturar_texto)
        audio_thread.start()
        texto_thread.start()

        # Espera até que uma resposta seja capturada
        timeout_event.wait()
        
        self.matar_thread(audio_thread)
        self.matar_thread(texto_thread)

        # Prioriza o áudio se disponível; caso contrário, usa o texto
        while not resposta_queue.empty():
            origem, resposta = resposta_queue.get()
            if origem == "audio":
                print(f"Usando resposta de áudio: {resposta}")
                return resposta
            elif origem == "texto":
                print(f"Usando resposta de texto: {resposta}")
                audio_thread = threading.Thread(target=capturar_audio)
                
                return resposta

        # Caso nenhuma entrada válida seja capturada
        print("Nenhuma entrada válida detectada.")
        return ""