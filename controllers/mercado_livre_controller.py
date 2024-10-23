# controllers/mercado_livre_controller.py
from models.mercado_livre_model import MercadoLivreModel
from views.view import View

class MercadoLivreController:
    def __init__(self):
        self.model = MercadoLivreModel()
        self.view = View()

    def buscar_produtos(self, descricao):
        criteria = {"descricao": descricao, "limite": 5}
        produtos = self.model.search_mercado_livre(criteria)
        self.view.exibir_produtos(produtos)
