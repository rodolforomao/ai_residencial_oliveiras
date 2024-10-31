# models/api_model.py
import requests
import datetime

class DateUtil:
    def __init__(self):
        pass
    
    def check_date(self, json_data):
        hoje = datetime.date.today()  # Data atual
        
        nova_data_start = None
        nova_data_end = None
        
        date_start = None
        date_end = None
        
        for dia in json_data['dias_ocupados']:
            # Converte strings para objetos de data
            date_start = datetime.datetime.strptime(dia['date_start'], '%Y-%m-%d').date()
            date_end = datetime.datetime.strptime(dia['date_end'], '%Y-%m-%d').date()
            
            # Verifica se o ano da data inicial é menor que o ano atual
            if date_start.year < hoje.year:
                # Ajusta o ano para o ano atual
                date_start = date_start.replace(year=hoje.year)
                date_end = date_end.replace(year=hoje.year)
            
            # Verifica se a data inicial é menor que a data atual
            if date_start < hoje:
                # Ajusta o mês
                novo_mes = hoje.month + 1 if hoje.month < 12 else 1
                novo_ano = hoje.year if hoje.month < 12 else hoje.year + 1
                
                # Atualiza data com novo mês e, se necessário, novo ano
                nova_data_start = date_start.replace(month=novo_mes, year=novo_ano)
                nova_data_end = date_end.replace(month=novo_mes, year=novo_ano)
                
        if nova_data_start is not None:
            json_data['dias_ocupados'][0]['date_start'] = nova_data_start.strftime('%Y-%m-%d')
        if nova_data_end is not None:
            json_data['dias_ocupados'][0]['date_end'] = nova_data_end.strftime('%Y-%m-%d')
            
        if date_start is not None:
            json_data['dias_ocupados'][0]['date_start'] = date_start.strftime('%Y-%m-%d')
        if date_end is not None:
            json_data['dias_ocupados'][0]['date_end'] = date_end.strftime('%Y-%m-%d')
            
        return json_data
    
    
    def check_date_agendar(self, json_data):
        hoje = datetime.date.today()  # Data atual
        
        nova_data_start = None
        nova_data_end = None
        
        date_start = None
        date_end = None
        
        index = 'appointment_details'
        appointment = json_data[index]
        
        # Converte strings para objetos de data
        date_start = datetime.datetime.strptime(appointment['date_start'], '%Y-%m-%d').date()
        date_end = datetime.datetime.strptime(appointment['date_end'], '%Y-%m-%d').date()
        
        # Verifica se o ano da data inicial é menor que o ano atual
        if date_start.year < hoje.year:
            # Ajusta o ano para o ano atual
            date_start = date_start.replace(year=hoje.year)
            date_end = date_end.replace(year=hoje.year)
        
        # Verifica se a data inicial é menor que a data atual
        if date_start < hoje:
            # Ajusta o mês
            novo_mes = hoje.month + 1 if hoje.month < 12 else 1
            novo_ano = hoje.year if hoje.month < 12 else hoje.year + 1
            
            # Atualiza data com novo mês e, se necessário, novo ano
            nova_data_start = date_start.replace(month=novo_mes, year=novo_ano)
            nova_data_end = date_end.replace(month=novo_mes, year=novo_ano)
                
        if nova_data_start is not None:
            json_data[index]['date_start'] = nova_data_start.strftime('%Y-%m-%d')
        if nova_data_end is not None:
            json_data[index]['date_end'] = nova_data_end.strftime('%Y-%m-%d')
            
        if date_start is not None:
            json_data[index]['date_start'] = date_start.strftime('%Y-%m-%d')
        if date_end is not None:
            json_data[index]['date_end'] = date_end.strftime('%Y-%m-%d')
            
        return json_data
    