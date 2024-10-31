# models/mercado_pago_model.py
import json
import requests
import mercadopago
import config.config as config

class MercadoPagoModel:
    
    def __init__(self):
        self.access_token = config.ACCESS_TOKEN_MERCADO_PAGO
    
    def generate_with_json(self, data):
        appointment_details = data['appointment_details']
        value = appointment_details['value']
        email = appointment_details['email']
        title = appointment_details['description']
        return self.generate_payment_link(title, value, email)
    
    def generate_payment_link(self, title, value, email):
        
        url = "https://api.mercadopago.com/checkout/preferences"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
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
                    "currency_id": "BRL",
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
