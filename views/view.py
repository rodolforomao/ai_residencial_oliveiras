# views/view.py
class View:
    def capturar_resposta(self, pergunta):
        return input(pergunta)

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
