# models/mercado_pago_model.py
import json
import requests
import mercadopago
import config.config as config

class MercadoPagoModel:
    
    def __init__(self):
        self.access_token = config.ACCESS_TOKEN_MERCADO_PAGO
        self.payment_id = None
        self.preference_id = None
    
    def generate_with_json(self, data):
        appointment_details = data['appointment_details']
        value = appointment_details['value']
        email = appointment_details['email']
        title = appointment_details['description']
        return self.generate_payment_link(title, value, email)
        
    def generate_payment_link(self, title, value, email):
        
        url = "https://api.mercadopago.com/checkout/preferences"
        headers = self.get_header()
        
        tag_currency = 'BRL'
        currency = tag_currency
        if 'R$' in value:
            value = value.replace('R$', '')
            currency = tag_currency
        else:
            tag_currency = 'USD'
            if tag_currency in value:
                value = value.replace(tag_currency, '')
                currency = tag_currency
            else:
                tag_currency = '$'
                if tag_currency in value:
                    value = value.replace(tag_currency, '')
                    currency = 'USD'
        
        try:
            unit_price = float(value.replace(',', ''))
        except ValueError:
            # Handle the error (e.g., set a default value or raise an error)
            unit_price = 0.0  # or some other logic
        
        preference_data = {
            "items": [
                {
                    "title": title,
                    "quantity": 1,
                    "currency_id": currency,
                    "unit_price": unit_price
                }
            ],
            "payer": {
                "email": email
            },
            "back_urls": {
                "success": "https://www.rodolforomao.com.br/residencialoliveiras/pagamento_sucesso",
                "failure": "https://www.rodolforomao.com.br/residencialoliveiras/pagamento_falha",
                "pending": "https://www.rodolforomao.com.br/residencialoliveiras/pagamento_pendente"
            },
            "auto_return": "approved"
        }
        
        response = requests.post(url, json=preference_data, headers=headers)
        
        if response.status_code == 201:
            data = response.json()
            init_point = data.get("init_point")
            sandbox_init_point = data.get("sandbox_init_point")
            print('Link: ' + init_point)
            print("Preferência criada com sucesso!")
            print("ID da preferência:", data.get("id"))
        else:
            error_data = response.json()
            error_message = error_data.get("message", "Erro desconhecido")
            error_cause = error_data.get("cause", [])
            
            print("Erro ao criar preferência:")
            print("Mensagem:", error_message)
            for cause in error_cause:
                print("Código do erro:", cause.get("code"))
                print("Descrição:", cause.get("description"))
       
        return response


    def get_header(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
    def check_payment_status(self, payment_id = None):
        if payment_id is None:
            payment_id = self.payment_id
            
        if payment_id is not None:
            url = f"https://api.mercadopago.com/v1/payments/{payment_id}"
            headers = self.get_header()
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                payment_info = response.json()
                status = payment_info.get("status")
                
                if status == "approved":
                    print("Pagamento aprovado.")
                    return True
                elif status == "pending":
                    print("Pagamento pendente.")
                    return False
                else:
                    print(f"Status do pagamento: {status}")
                    return False
            else:
                print("Erro ao verificar status do pagamento.")
                return False
        
        print("Informe o id do pagamento para verificar o status.")
        return False
    

    def check_payment_status_preference_id(self, preference_id):
        if preference_id is None:
            preference_id = self.preference_id

        url = f"https://api.mercadopago.com/checkout/preferences/{preference_id}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        #response = requests.get(url, headers=headers, params=params)
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            payments = response.json().get("results", [])
            if payments:
                for payment in payments:
                    if payment["status"] == "approved":
                        print("Pagamento aprovado!")
                        return True
                print("Nenhum pagamento aprovado encontrado.")
                return False
            else:
                print("Nenhum pagamento encontrado para este preference_id.")
                return False
        else:
            print("Erro ao verificar o status do pagamento:", response.json())
            return False