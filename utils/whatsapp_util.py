# utils/whatsapp_util.py

import os
import re
import sys
import json
import hashlib
from datetime import datetime, timedelta

sys.path.append(r'C:\desenvolvimento\Estudos\IA\integracao_via_web\gpt_whats_chabot')
from application.util.files import Files



class WhatsappUtils:
    
    INDEX_OBJECT_MESSAGES = 'messages'
    INDEX_OBJECT_TEXT_MESAGE = 'text'
    INDEX_OBJECT_RUN_ID = 'run_id'
    INDEX_OBJECT_THREAD_ID = 'thread_id'
    
    def __init__(self):
        pass

    def get_unread_msg_text(self, text, cellphone_number):
        conversa_object = self.get_conversation_and_save(text, cellphone_number, only_unread=True)
        msg_output = ""
        for msg in conversa_object.get(self.INDEX_OBJECT_MESSAGES, []):
            msg_output += msg.get(self.INDEX_OBJECT_TEXT_MESAGE) + '.\n'
        return msg_output

    def get_conversation_and_save(self, text, cellphone_number, only_unread = False, run_id=None, thread_id=None,):
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
        with open(filename, 'r', encoding='utf-8') as f:
            conversa_object = json.load(f)
        return conversa_object
    
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