# utils/whatsapp_util.py

import os
import re
import sys
import json
import hashlib
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

from utils.string_util import StringUtil

sys.path.append(r'C:\desenvolvimento\Estudos\IA\integracao_via_web\gpt_whats_chabot')
from application.util.files import Files



class WhatsappUtils:
    
    INDEX_OBJECT_MESSAGES = 'messages'
    INDEX_OBJECT_TEXT_MESAGE = 'text'
    INDEX_OBJECT_RUN_ID = 'run_id'
    INDEX_OBJECT_THREAD_ID = 'thread_id'
    
    def __init__(self):
        pass

    def get_unread_msg_text(self, text, cellphone_number, html = None, is_user = True):
        conversa_object = self.get_conversation_and_save(text, cellphone_number, only_unread=True, run_id=None, thread_id=None, html=html, is_user = is_user)
        msg_output = ""
        for msg in conversa_object.get(self.INDEX_OBJECT_MESSAGES, []):
            msg_output += msg.get(self.INDEX_OBJECT_TEXT_MESAGE) + '.\n'
        return msg_output

    def get_conversation_and_save(self, text, cellphone_number, only_unread = False, run_id=None, thread_id=None, html=None, is_user = True):
        if html:
            #new_object = self.parse_conversations_html(text, cellphone_number, html)
            new_object = self.parse_conversations_html_2(text, cellphone_number, html, is_user)
            
        else:
            new_object = self.parse_conversations(text, cellphone_number)
            
        if run_id is not None:
            new_object[self.INDEX_OBJECT_RUN_ID] = run_id
        if thread_id is not None:
            new_object[self.INDEX_OBJECT_THREAD_ID] = thread_id
        unread_conversation = None
        if only_unread:
            unread_conversation = self.get_unread(new_object)
            new_object = self.set_all_as_read(new_object)
        self.save_conversation_as_json(new_object, cellphone_number)
        if only_unread:
            return unread_conversation
        return new_object
    
    def get_file_in_json(self, filename):
        filename = self.get_file_name_of_json(filename)
        conversa_object = None
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                conversa_object = json.load(f)
        return conversa_object
    
    def get_file_name_all_jsons(self, folder_path = 'files/history', last_message_skip = True):
        json_objects = []
    
        return os.listdir(folder_path)
    
    def get_exists_conversation_and_update_thread_run(self, filename, run_id=None, thread_id=None,):
        conversa_object = self.get_file_in_json(filename)
        
        if conversa_object:
            if run_id is not None:
                conversa_object[self.INDEX_OBJECT_RUN_ID] = run_id
            if thread_id is not None:
                conversa_object[self.INDEX_OBJECT_THREAD_ID] = thread_id
            self.save_conversation_as_json(conversa_object, filename)
        return conversa_object
    
    def get_unread(self, conversa_object):
        unread_conversation = {
            'cell_number': conversa_object.get('cell_number'),
            'name': conversa_object.get('name'),
            'email': conversa_object.get('email'),
            self.INDEX_OBJECT_RUN_ID: conversa_object.get(self.INDEX_OBJECT_RUN_ID),
            self.INDEX_OBJECT_THREAD_ID: conversa_object.get(self.INDEX_OBJECT_THREAD_ID),
            'title': conversa_object.get('title'),
            self.INDEX_OBJECT_MESSAGES: [msg for msg in conversa_object.get(self.INDEX_OBJECT_MESSAGES, []) if msg.get('unread', False)]
        }

        return unread_conversation

    def set_all_as_read(self, conversa_object):
        if self.INDEX_OBJECT_MESSAGES in conversa_object:
            for msg in conversa_object[self.INDEX_OBJECT_MESSAGES]:
                msg['unread'] = False
        return conversa_object

    def get_file_name_of_json(self, filename):
        filename = self.add_json_extension(filename)
        default_folder = "files/history/"
        if default_folder not in filename:
            filename = "files/history/" + filename
        return filename

    def save_conversation_as_json(self, new_object, filename='conversation.json'):
        filename = self.get_file_name_of_json(filename)
        file = Files()
        file.ensure_directory_exists_add_slash(filename)
        
        if not new_object:
            print("Nenhuma conversa encontrada para salvar.")
            return
        
        try:
            existing_object = self.get_file_in_json(filename)
            existing_hash = self.compute_hash(existing_object)
        except FileNotFoundError:
            existing_object = None
            existing_hash = None
        
        ##########
        # Mantem o thread_id e run_id caso não existam no novo objeto, caso exista, atualiza os valores do thread_id e run_id
        ##########
        if existing_object:
            index = "run_id"
            new_object[index] = new_object.get(index) or existing_object.get(index)
            index = "thread_id"
            new_object[index] = new_object.get(index) or existing_object.get(index)
            index = "email"
            new_object[index] = new_object.get(index) or existing_object.get(index)
            index = "name"
            new_object[index] = new_object.get(index) or existing_object.get(index)
        
        new_hash = self.compute_hash(new_object)
        
        if existing_object and existing_hash != new_hash:
            existing_messages = existing_object.get("messages", [])
            new_messages = new_object.get("messages", [])
            
            existing_messages_dict = {msg['datetime'] + msg[self.INDEX_OBJECT_TEXT_MESAGE]: msg for msg in existing_messages}
            
            for msg in new_messages:
                if 'ONTEM\n' in msg:
                    print('')
                unique_key = msg['datetime'] + msg[self.INDEX_OBJECT_TEXT_MESAGE]
                if unique_key not in existing_messages_dict:
                    existing_messages_dict[unique_key] = msg
            
            combined_messages = list(existing_messages_dict.values())
            new_object["messages"] = combined_messages
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(new_object, f, ensure_ascii=False, indent=4)
        print(f"Conversa salva em {filename}")


    def compute_hash(self, obj):
        """Compute the hash of the JSON object."""
        return hashlib.md5(json.dumps(obj, sort_keys=True).encode()).hexdigest()
    
    
    def parse_conversations(self, text, cell_number):
        
        #text = text.replace('\nHOJE\n', '\n')
        hoje_count = text.count('HOJE')
        if hoje_count > 1:
            text = text.replace('\nHOJE\n', '\n', 1)
        tag_date_today = '[Date:' + datetime.now().strftime("%Y-%m-%d") + ']'
        text = text.replace('\nHOJE\n', '\n'+tag_date_today+'\n', 1)

        pattern = r"^([^\n]+)\n([^\n]+)\n"
        msg_pattern = r"([^\n]+(?:\n[^\n]+)*?)\n(\d{2}:\d{2})"
        unread_msg_pattern = r"\b\d+\s*MENSAGENS?\s*NÃO\s*LIDAS\b|\b\d+\s*UNREAD\s*MESSAGES?\b"
        match = re.search(pattern, text, re.DOTALL)

        if match:
            nome = match.group(1)
            titulo = match.group(2)
            messages = []
            restante_texto = text[match.end():]
            unread = False
            data_hoje = None
            
            for m in re.finditer(msg_pattern, restante_texto):
                mensagem = m.group(1)
                if tag_date_today.strip() in mensagem:
                    mensagem = mensagem.replace(tag_date_today,'')
                    data_hoje = datetime.now().strftime("%Y-%m-%d")
                    
                if 'MENSAGEM NÃO LIDA' in mensagem or 'UNREAD MESSAGE' in mensagem  or 'MENSAGENS NÃO LIDAS' in mensagem:
                    mensagem = mensagem.replace('1 MENSAGEM NÃO LIDA','')
                    unread = True
                mensagem = re.sub(unread_msg_pattern, "", mensagem).strip()
                time_msg = m.group(2)

                if data_hoje:
                    timestamp = f"{data_hoje} {time_msg}"
                    datetime_obj = datetime.strptime(timestamp, "%Y-%m-%d %H:%M")
                    datetime_obj = datetime_obj.strftime("%Y-%m-%d %H:%M")
                else:
                    datetime_obj = f"{time_msg}"

                messages.append({
                    "text": mensagem,
                    # "datetime": datetime_obj.strftime("%Y-%m-%d %H:%M"),
                    "datetime": datetime_obj,
                    "unread": unread,
                    "answered": False,
                    })
            objeto = {
                "cell_number": cell_number,
                "name": nome,
                'email': None,
                self.INDEX_OBJECT_RUN_ID: None,
                self.INDEX_OBJECT_THREAD_ID: None,
                "title": titulo,
                "messages": messages                
            }
        return objeto
    
    def parse_conversations_html(self, text, cell_number, html):
        
        #text = text.replace('\nHOJE\n', '\n')
        hoje_count = text.count('HOJE')
        if hoje_count > 1:
            text = text.replace('\nHOJE\n', '\n', 1)
        tag_date_today = '[Date:' + datetime.now().strftime("%Y-%m-%d") + ']'
        text = text.replace('\nHOJE\n', '\n'+tag_date_today+'\n', 1)

        pattern = r"^([^\n]+)\n([^\n]+)\n"
        msg_pattern = r"([^\n]+(?:\n[^\n]+)*?)\n(\d{2}:\d{2})"
        unread_msg_pattern = r"\b\d+\s*MENSAGENS?\s*NÃO\s*LIDAS\b|\b\d+\s*UNREAD\s*MESSAGES?\b"
        match = re.search(pattern, text, re.DOTALL)

        if match:
            nome = match.group(1)
            titulo = match.group(2)
            messages = []
            restante_texto = text[match.end():]
            unread = False
            data_hoje = None
            
            for m in re.finditer(msg_pattern, restante_texto):
                mensagem = m.group(1)
                if tag_date_today.strip() in mensagem:
                    mensagem = mensagem.replace(tag_date_today,'')
                    data_hoje = datetime.now().strftime("%Y-%m-%d")
                    
                if 'MENSAGEM NÃO LIDA' in mensagem or 'UNREAD MESSAGE' in mensagem  or 'MENSAGENS NÃO LIDAS' in mensagem:
                    mensagem = mensagem.replace('1 MENSAGEM NÃO LIDA','')
                    unread = True
                mensagem = re.sub(unread_msg_pattern, "", mensagem).strip()
                time_msg = m.group(2)

                new_object = self.get_object_title_message_2(mensagem)
                nome = None
                if new_object:
                    nome = new_object.get('nome')
                    tipo = self.identificar_tipo_mensagem(html, new_object.get('conteudo'))
                else:
                    nome = 'you'
                    tipo = self.identificar_tipo_mensagem(html, mensagem)

                if data_hoje:
                    timestamp = f"{data_hoje} {time_msg}"
                    datetime_obj = datetime.strptime(timestamp, "%Y-%m-%d %H:%M")
                    datetime_obj = datetime_obj.strftime("%Y-%m-%d %H:%M")
                else:
                    datetime_obj = f"{time_msg}"

                messages.append({
                    "text": mensagem,
                    "sender": nome,
                    # "datetime": datetime_obj.strftime("%Y-%m-%d %H:%M"),
                    "datetime": datetime_obj,
                    "unread": unread,
                    "answered": False,
                    "in_out": tipo
                    })
            objeto = {
                "cell_number": cell_number,
                "name": nome,
                'email': None,
                self.INDEX_OBJECT_RUN_ID: None,
                self.INDEX_OBJECT_THREAD_ID: None,
                "title": titulo,
                "messages": messages                
            }
        return objeto
    
    def get_greater_msg(self, mensagem):
        msg = ''
        index = -1
        size = -1
        for item in mensagem:
            if len(item) > size:
                size = len(item)
                msg = item
                index = mensagem.index(item)
        return msg
            
    def identificar_tipo_mensagem(self, html, mensagem):
        # Parse do HTML com BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        mensagem = self.get_greater_msg(mensagem)
        # Encontre o elemento que contém a mensagem
        #mensagem_elemento = soup.find_all(string=mensagem)
        mensagem_elemento = soup.find_all(text=re.compile(re.escape(mensagem), re.IGNORECASE))
        
        if not mensagem_elemento:
            return "Mensagem não encontrada"
        
        # Itera sobre os elementos encontrados que contêm a mensagem
        for elem in mensagem_elemento:
            # Verifica as classes do elemento ou de seus ancestrais
            parent = elem.find_parent()
            
            # Verificar a classe dos elementos ancestrais (como pais e avós)
            while parent:
                if 'message-in' in parent.get('class', []):
                    return 'mensagem-in'
                elif 'message-out' in parent.get('class', []):
                    return 'message-out'
                elif 'alert' in parent.get('data-icon', ''):
                    return 'alerta'
                elif '_amk4' in parent.get('class', []) and '_ao3e' in parent.get('class', []):
                    return 'datas'
                
                # Subir para o próximo ancestral
                parent = parent.find_parent()
        
        return "Tipo de mensagem desconhecido"
    
    def add_json_extension(self, filename):
        filename = str(filename)
        if not os.path.splitext(filename)[1]:
            return filename + ".json"
        return filename

    def get_thread_and_run_ids(self, filename):
        filename = self.get_file_name_of_json(filename)
        conversa_object = self.get_file_in_json(filename)
        if conversa_object:
            thread_id = conversa_object.get(self.INDEX_OBJECT_THREAD_ID)
            run_id = conversa_object.get(self.INDEX_OBJECT_RUN_ID)
            return thread_id, run_id
        return None, None
    
    
    def get_object_title_message(self, text):
        text_lines = text.split('\n')
        if len(text_lines):
            if len(text_lines) == 5:
                # Grupo
                nome = text_lines[0].strip()
                horario = text_lines[1].strip()
                remetente = text_lines[2].strip()
                if 'Rascunho' in remetente or 'Draft' in remetente:
                    return None
                separador = text_lines[3].strip()
                conteudo = text_lines[4].strip()
                return {
                    "nome": nome,
                    "horario": horario,
                    "remetente": remetente,
                    "conteudo": conteudo,
                    "separador": separador,
                    "is_user": False,
                }
            elif len(text_lines) == 4:
                 # Grupo
                nome = text_lines[0].strip()
                value = text_lines[1].strip()
                if 'você' in value.lower() or 'you' in value.lower():
                    remetente = 'you'
                    horario = text_lines[2].strip()
                    conteudo = text_lines[3].strip()
                else:
                    remetente = nome
                    horario = text_lines[1].strip()
                    conteudo = text_lines[2].strip()
                return {
                    "nome": nome,
                    "horario": horario,
                    "remetente": remetente,
                    "conteudo": conteudo,
                    "separador": None,
                    "is_user": True,
                }
            elif len(text_lines) == 3:
                # Usuário
                nome = text_lines[0].strip()
                horario = text_lines[1].strip()
                conteudo = text_lines[2].strip()
                return {
                    "nome": nome,
                    "horario": horario,
                    "remetente": nome,
                    "conteudo": conteudo,
                    "separador": None,
                    "is_user": True,
                }
    
    def get_object_title_message_2(self, text):
        text_lines = text.split('\n')
        if len(text_lines):
            if len(text_lines) >= 5:
                # Grupo
                nome = text_lines[0].strip()
                value = text_lines[1].strip()
                is_foward = 'encaminhada'.lower() in value.lower()
                if is_foward:
                    horario = text_lines[2].strip()
                else:
                    horario = value
            
                index = 2
                if is_foward:
                    index = 3
                    
                conteudo = [line.strip() for line in text_lines[index:]]
                
                # if 'Rascunho' in remetente or 'Draft' in remetente:
                #     return None
                # separador = text_lines[3].strip()
                # #conteudo = text_lines[4].strip()
                # conteudo = " ".join(line.strip() for line in text_lines[3:])
                
                return {
                    "nome": nome,
                    "horario": horario,
                    "remetente": nome,
                    "conteudo": conteudo,
                    "separador": None,
                    "is_user": False,
                }
            elif len(text_lines) == 3:
                # Usuário
                nome = text_lines[0].strip()
                horario = text_lines[1].strip()
                conteudo = text_lines[2].strip()
                return {
                    "nome": nome,
                    "horario": horario,
                    "remetente": nome,
                    "conteudo": conteudo,
                    "separador": None,
                    "is_user": True,
                }
    
    def message_exists(self, new_object, filename):
        if new_object:
            
            mensagem_obj = {
                "text": new_object.get('conteudo'),
                "datetime": new_object.get('horario')
            }

            # Verificar se já existe no JSON
            conversa_obj = self.get_file_in_json(filename)
            if not conversa_obj:
                return False

            string_util = StringUtil()
            for msg in conversa_obj.get(self.INDEX_OBJECT_MESSAGES, []):
                if string_util.normalize(mensagem_obj["text"]) in string_util.normalize(msg["text"]) and string_util.normalize(mensagem_obj["datetime"]) in string_util.normalize(msg["datetime"]):
                    return True
        return False
    
    
    # def save_conversation_as_json(self, new_object, filename='conversation.json'):
    #     filename = self.get_file_name_of_json(filename)
    #     file = Files()
    #     file.ensure_directory_exists_add_slash(filename)
        
    #     if not new_object:
    #         print("Nenhuma conversa encontrada para salvar.")
    #         return
        
    #     try:
    #         existing_object = self.get_file_in_json(filename)
    #         existing_hash = self.compute_hash(existing_object)
    #     except FileNotFoundError:
    #         existing_object = None
    #         existing_hash = None
        
    #     ##########
    #     # Mantem o thread_id e run_id caso não existam no novo objeto, caso exista, atualiza os valores do thread_id e run_id
    #     ##########
    #     if existing_object:
    #         index = "run_id"
    #         new_object[index] = new_object.get(index) or existing_object.get(index)
    #         index = "thread_id"
    #         new_object[index] = new_object.get(index) or existing_object.get(index)
    #         index = "email"
    #         new_object[index] = new_object.get(index) or existing_object.get(index)
    #         index = "name"
    #         new_object[index] = new_object.get(index) or existing_object.get(index)
        
    #     new_hash = self.compute_hash(new_object)
        
    #     if existing_object and existing_hash != new_hash:
    #         existing_messages = existing_object.get("messages", [])
    #         new_messages = new_object.get("messages", [])
            
    #         existing_messages_dict = {msg['datetime'] + msg[self.INDEX_OBJECT_TEXT_MESAGE]: msg for msg in existing_messages}
            
    #         for msg in new_messages:
    #             unique_key = msg['datetime'] + msg[self.INDEX_OBJECT_TEXT_MESAGE]
    #             if unique_key not in existing_messages_dict:
    #                 existing_messages_dict[unique_key] = msg
            
    #         combined_messages = list(existing_messages_dict.values())
    #         new_object["messages"] = combined_messages
        
    #     with open(filename, 'w', encoding='utf-8') as f:
    #         json.dump(new_object, f, ensure_ascii=False, indent=4)
    #     print(f"Conversa salva em {filename}")


    def compute_hash(self, obj):
        """Compute the hash of the JSON object."""
        return hashlib.md5(json.dumps(obj, sort_keys=True).encode()).hexdigest()
    
    
    def parse_conversations(self, text, cell_number):
        
        #text = text.replace('\nHOJE\n', '\n')
        hoje_count = text.count('HOJE')
        if hoje_count > 1:
            text = text.replace('\nHOJE\n', '\n', 1)
        tag_date_today = '[Date:' + datetime.now().strftime("%Y-%m-%d") + ']'
        text = text.replace('\nHOJE\n', '\n'+tag_date_today+'\n', 1)

        pattern = r"^([^\n]+)\n([^\n]+)\n"
        msg_pattern = r"([^\n]+(?:\n[^\n]+)*?)\n(\d{2}:\d{2})"
        unread_msg_pattern = r"\b\d+\s*MENSAGENS?\s*NÃO\s*LIDAS\b|\b\d+\s*UNREAD\s*MESSAGES?\b"
        match = re.search(pattern, text, re.DOTALL)

        if match:
            nome = match.group(1)
            titulo = match.group(2)
            messages = []
            restante_texto = text[match.end():]
            unread = False
            data_hoje = None
            
            for m in re.finditer(msg_pattern, restante_texto):
                mensagem = m.group(1)
                if tag_date_today.strip() in mensagem:
                    mensagem = mensagem.replace(tag_date_today,'')
                    data_hoje = datetime.now().strftime("%Y-%m-%d")
                    
                if 'MENSAGEM NÃO LIDA' in mensagem or 'UNREAD MESSAGE' in mensagem  or 'MENSAGENS NÃO LIDAS' in mensagem:
                    mensagem = mensagem.replace('1 MENSAGEM NÃO LIDA','')
                    unread = True
                mensagem = re.sub(unread_msg_pattern, "", mensagem).strip()
                time_msg = m.group(2)

                if data_hoje:
                    timestamp = f"{data_hoje} {time_msg}"
                    datetime_obj = datetime.strptime(timestamp, "%Y-%m-%d %H:%M")
                    datetime_obj = datetime_obj.strftime("%Y-%m-%d %H:%M")
                else:
                    datetime_obj = f"{time_msg}"

                messages.append({
                    "text": mensagem,
                    # "datetime": datetime_obj.strftime("%Y-%m-%d %H:%M"),
                    "datetime": datetime_obj,
                    "unread": unread,
                    "answered": False,
                    })
            objeto = {
                "cell_number": cell_number,
                "name": nome,
                'email': None,
                self.INDEX_OBJECT_RUN_ID: None,
                self.INDEX_OBJECT_THREAD_ID: None,
                "title": titulo,
                "messages": messages                
            }
        return objeto
    
    def parse_conversations_html(self, text, cell_number, html):
        
        #text = text.replace('\nHOJE\n', '\n')
        hoje_count = text.count('HOJE')
        if hoje_count > 1:
            text = text.replace('\nHOJE\n', '\n', 1)
        tag_date_today = '[Date:' + datetime.now().strftime("%Y-%m-%d") + ']'
        text = text.replace('\nHOJE\n', '\n'+tag_date_today+'\n', 1)

        pattern = r"^([^\n]+)\n([^\n]+)\n"
        msg_pattern = r"([^\n]+(?:\n[^\n]+)*?)\n(\d{2}:\d{2})"
        unread_msg_pattern = r"\b\d+\s*MENSAGENS?\s*NÃO\s*LIDAS\b|\b\d+\s*UNREAD\s*MESSAGES?\b"
        match = re.search(pattern, text, re.DOTALL)

        if match:
            nome = match.group(1)
            titulo = match.group(2)
            messages = []
            restante_texto = text[match.end():]
            unread = False
            data_hoje = None
            
            for m in re.finditer(msg_pattern, restante_texto):
                mensagem = m.group(1)
                if tag_date_today.strip() in mensagem:
                    mensagem = mensagem.replace(tag_date_today,'')
                    data_hoje = datetime.now().strftime("%Y-%m-%d")
                    
                if 'MENSAGEM NÃO LIDA' in mensagem or 'UNREAD MESSAGE' in mensagem  or 'MENSAGENS NÃO LIDAS' in mensagem:
                    mensagem = mensagem.replace('1 MENSAGEM NÃO LIDA','')
                    unread = True
                mensagem = re.sub(unread_msg_pattern, "", mensagem).strip()
                time_msg = m.group(2)

                new_object = self.get_object_title_message_2(mensagem)
                nome = None
                if new_object:
                    nome = new_object.get('nome')
                    tipo = self.identificar_tipo_mensagem(html, new_object.get('conteudo'))
                else:
                    nome = 'you'
                    tipo = self.identificar_tipo_mensagem(html, mensagem)

                if data_hoje:
                    timestamp = f"{data_hoje} {time_msg}"
                    datetime_obj = datetime.strptime(timestamp, "%Y-%m-%d %H:%M")
                    datetime_obj = datetime_obj.strftime("%Y-%m-%d %H:%M")
                else:
                    datetime_obj = f"{time_msg}"

                messages.append({
                    "text": mensagem,
                    "sender": nome,
                    # "datetime": datetime_obj.strftime("%Y-%m-%d %H:%M"),
                    "datetime": datetime_obj,
                    "unread": unread,
                    "answered": False,
                    "in_out": tipo
                    })
            objeto = {
                "cell_number": cell_number,
                "name": nome,
                'email': None,
                self.INDEX_OBJECT_RUN_ID: None,
                self.INDEX_OBJECT_THREAD_ID: None,
                "title": titulo,
                "messages": messages                
            }
        return objeto
    
    
    def parse_conversations_html_2(self, text, cell_number, html_content, is_user = True):
        
        soup = BeautifulSoup(html_content, 'html.parser')

        profile_button = soup.find('div', {'title': 'Dados de perfil', 'role': 'button'})
        name = profile_button.find_next('span', {'class': '_ao3e'}).text
        element = profile_button.find_next('span', {'class': 'selectable-text copyable-text'})
        members_list = None
        if element:
            members_list = element.text
            
        # Finding all rows (messages)
        rows = soup.find_all('div', role="row")
        messages = []

        for row in rows:
            
            # Locate the sender's name by identifying the unique class
            sender_name_tag = row.find('span', {'class': '_ahxt x1ypdohk xt0b8zv _ao3e'})
            if sender_name_tag:
                sender_name = sender_name_tag.get_text(strip=True)
                print("Sender Name:", sender_name)
            else:
                print("Sender Name not found.")
                sender_name = name

            
            message_container = row.find('div', class_=['message-in', 'message-out'])
            if not message_container:
                continue  # Skip if message container is not found

            in_out = 'in' if 'message-in' in message_container['class'] else 'out'

            # Extract message content
            message_span = row.find('span', class_='_ao3e selectable-text copyable-text')

            # Check if message_span was found and extract text
            message_text = None
            if message_span and message_span.text.strip():
                message_text = message_span.text.strip()

            # Extract datetime of the message
            datetime_text = message_container.find('div', class_='copyable-text')
            datetime_info = datetime_text.get('data-pre-plain-text', '') if datetime_text else ''
            message_datetime = datetime_info.split(']')[0].strip('[')  # Extracting date and time part
            if message_datetime:
                datetime_obj = datetime.strptime(message_datetime, '%H:%M, %d/%m/%Y')
                formatted_datetime = datetime_obj.strftime('%Y-%m-%d %H:%M')
            if not message_datetime:
                time_span = soup.find('span', class_='x1rg5ohu x16dsc37')
                formatted_datetime = time_span.text if time_span else 'Time not found'
                
            if message_text:
                message_type = 'text'
            
            type_audio = row.find(lambda tag: tag.get('aria-label') == "Mensagem de voz" or tag.get('data-icon') == "ptt-file")
            if not type_audio:
                type_audio = row.find('input', {'aria-label': lambda x: x and 'Duração' in x})
            
            if type_audio:
                message_type = 'audio'
                duration_element = soup.find('input', {'aria-label': True})
                if duration_element:
                    duration_text = duration_element['aria-label']
                    duration = duration_text.split(':')[-1].strip()  # Extracts "0:08" or similar format
                    print("Audio duration:", duration)
                else:
                    print("Audio duration not found.")
            elif row.find('video'):
                message_type = 'video'
            elif row.find('img'):
                img_tag = row.find("img")
                if img_tag and "emoji" not in img_tag.get("class", []):
                    message_type = 'image'
                
            # Extract number_id from data-id attribute
            number_id = message_container.get('data-id', cell_number)  # Use cell_number if not found

            # Append the parsed information to conversations list
            messages.append({
                'number_id': number_id,
                'name': sender_name,
                'datetime': formatted_datetime,
                'in_out': in_out,
                'message': message_text,
                'message_type': message_type,
                'answered': None,
            })

        objeto = {
                "cell_number": cell_number,
                "name": name,
                'email': None,
                self.INDEX_OBJECT_RUN_ID: None,
                self.INDEX_OBJECT_THREAD_ID: None,
                "title": name,
                "messages": messages                
            }
        return objeto 
    
    
    def get_greater_msg(self, mensagem):
        
        msg = ''
        index = -1
        size = -1
        for item in mensagem:
            if self.check_default_messages(item):
                continue
            if len(item) > size:
                size = len(item)
                msg = item
                index = mensagem.index(item)
        return msg
    
    def check_default_messages(self, message):
        skip_messages = ['Use o WhatsApp no seu celular para ver mensagens enviadas e rece'
                        ,'As mensagens são protegidas com a criptografia de ponta a ponta'
                        ,'Esta empresa usa um serviço seguro da empresa Meta para gerenciar'
                        ,'As mensagens são protegidas com a criptografia de ponta a ponta'
                        ,'mudou a descrição do grupo. Clique para mostrar']
        for skip_item in skip_messages:
            if skip_item in message:
                return True
        return False
            
    def identificar_tipo_mensagem(self, html, mensagem):
        soup = BeautifulSoup(html, 'html.parser')

        if type(mensagem) != str:
            mensagem = self.get_greater_msg(mensagem)
        mensagem_elemento = soup.find_all(text=re.compile(re.escape(mensagem), re.IGNORECASE))
        
        if not mensagem_elemento:
            return "Mensagem não encontrada"
        
        if self.check_default_messages(mensagem):
            return 'alerta'
        
        # Itera sobre os elementos encontrados que contêm a mensagem
        for elem in mensagem_elemento:
            # Verifica as classes do elemento ou de seus ancestrais
            parent = elem.find_parent()
            
            # Verificar a classe dos elementos ancestrais (como pais e avós)
            while parent:
                if 'message-in' in parent.get('class', []):
                    return 'mensagem-in'
                elif 'message-out' in parent.get('class', []):
                    return 'message-out'
                elif 'alert' in parent.get('data-icon', ''):
                    return 'alerta'
                elif '_amk4' in parent.get('class', []) and '_ao3e' in parent.get('class', []):
                    return 'datas'
                
                # Subir para o próximo ancestral
                parent = parent.find_parent()
        
        return "Tipo de mensagem desconhecido"
    
    def add_json_extension(self, filename):
        filename = str(filename)
        if not os.path.splitext(filename)[1]:
            return filename + ".json"
        return filename

    def get_thread_and_run_ids(self, filename):
        filename = self.get_file_name_of_json(filename)
        conversa_object = self.get_file_in_json(filename)
        if conversa_object:
            thread_id = conversa_object.get(self.INDEX_OBJECT_THREAD_ID)
            run_id = conversa_object.get(self.INDEX_OBJECT_RUN_ID)
            return thread_id, run_id
        return None, None
    
    
    def get_object_title_message(self, text):
        text_lines = text.split('\n')
        if len(text_lines):
            if len(text_lines) == 5:
                # Grupo
                nome = text_lines[0].strip()
                horario = text_lines[1].strip()
                remetente = text_lines[2].strip()
                if 'Rascunho' in remetente or 'Draft' in remetente:
                    return None
                separador = text_lines[3].strip()
                conteudo = text_lines[4].strip()
                return {
                    "nome": nome,
                    "horario": horario,
                    "remetente": remetente,
                    "conteudo": conteudo,
                    "separador": separador,
                    "is_user": False,
                }
            elif len(text_lines) == 4:
                 # Grupo
                nome = text_lines[0].strip()
                value = text_lines[1].strip()
                if 'você' in value.lower() or 'you' in value.lower():
                    remetente = 'you'
                    horario = text_lines[2].strip()
                    conteudo = text_lines[3].strip()
                else:
                    remetente = nome
                    horario = text_lines[1].strip()
                    conteudo = text_lines[2].strip()
                return {
                    "nome": nome,
                    "horario": horario,
                    "remetente": remetente,
                    "conteudo": conteudo,
                    "separador": None,
                    "is_user": True,
                }
            elif len(text_lines) == 3:
                # Usuário
                nome = text_lines[0].strip()
                horario = text_lines[1].strip()
                conteudo = text_lines[2].strip()
                return {
                    "nome": nome,
                    "horario": horario,
                    "remetente": nome,
                    "conteudo": conteudo,
                    "separador": None,
                    "is_user": True,
                }
    
    def get_object_title_message_2(self, text):
        text_lines = text.split('\n')
        if len(text_lines):
            if len(text_lines) >= 5:
                # Grupo
                nome = text_lines[0].strip()
                value = text_lines[1].strip()
                is_foward = 'encaminhada'.lower() in value.lower()
                if is_foward:
                    horario = text_lines[2].strip()
                else:
                    horario = value
            
                index = 2
                if is_foward:
                    index = 3
                    
                conteudo = [line.strip() for line in text_lines[index:]]
                
                # if 'Rascunho' in remetente or 'Draft' in remetente:
                #     return None
                # separador = text_lines[3].strip()
                # #conteudo = text_lines[4].strip()
                # conteudo = " ".join(line.strip() for line in text_lines[3:])
                
                return {
                    "nome": nome,
                    "horario": horario,
                    "remetente": nome,
                    "conteudo": conteudo,
                    "separador": None,
                    "is_user": False,
                }
            elif len(text_lines) == 3:
                # Usuário
                nome = text_lines[0].strip()
                horario = text_lines[1].strip()
                conteudo = text_lines[2].strip()
                return {
                    "nome": nome,
                    "horario": horario,
                    "remetente": nome,
                    "conteudo": conteudo,
                    "separador": None,
                    "is_user": True,
                }
    
    def save_conversation_as_json_manager_list(self, new_object, filename='conversation.json'):
        filename = self.get_file_name_of_json(filename)
        file = Files()
        file.ensure_directory_exists_add_slash(filename)
        
        if not new_object:
            print("Nenhuma conversa encontrada para salvar.")
            return
        
        try:
            existing_object = self.get_file_in_json(filename)
            existing_hash = self.compute_hash(existing_object)
        except FileNotFoundError:
            existing_object = None
            existing_hash = None
        
        new_hash = self.compute_hash(new_object)
        
        if existing_hash != new_hash:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(new_object, f, ensure_ascii=False, indent=4)
            print(f"Conversa salva em {filename}")