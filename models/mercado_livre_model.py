# models/mercado_livre_model.py
import requests

class MercadoLivreModel:
    @staticmethod
    def search_mercado_livre(criteria):
        url = "https://api.mercadolibre.com/sites/MLB/search"
        descricao = criteria.get("descricao")
        limite = criteria.get("limite", 5)
        params = {"q": descricao, "limit": limite}
        response = requests.get(url, params=params)
        return response.json()
