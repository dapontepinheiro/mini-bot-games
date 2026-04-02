# MiniGames Telegram Bot 🤖🎮
Bot de telegram desenvolvido com Python junto à API Telebot, feito para você desafiar e se divertir com o chatbot em minigames variados.

## 🕹️ Jogos Disponíveis
Jogo da Velha - Desafie o bot no clássico jogo da velha

Forca - Adivinhe a palavra secreta antes de ser enforcado

Batalha Naval - Trave uma batalha naval contra o bot e tente afundar seus navios

## 🖥️ Comandos Principais
/start - Mostra o menu principal

/games - Lista todos os jogos disponíveis

/forca - Inicia um novo jogo de forca com uma senha aleatória

/velha - Inicia um novo jogo da velha

/batalha - Inicia um novo jogo de batalha naval

## ⚙️ Como Executar

1. Clone o repositório e instale as dependências
```bash
pip install -r requirements.txt
```

2. Crie um bot no Telegram via [@BotFather](https://t.me/botfather) e copie o token gerado

3. Crie um arquivo `.env` na raiz do projeto
```
MINIGAME_TOKENN=seu_token_aqui
```

4. Execute o bot
```bash
python minibotgames.py
```
