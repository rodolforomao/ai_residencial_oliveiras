#!/bin/bash

# Cria as pastas para o projeto MVC
mkdir -p project/{config,controllers,models,views}

# Cria arquivos iniciais para o MVC
touch project/config/config.py
touch project/controllers/main_controller.py
touch project/controllers/mercado_livre_controller.py
touch project/models/api_model.py
touch project/models/mercado_livre_model.py
touch project/views/view.py
touch project/main.py


pip install -r requirements.txt


pip install mercadopago
