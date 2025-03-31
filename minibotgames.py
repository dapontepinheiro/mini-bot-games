import telebot, random, time
from collections import defaultdict
from telebot.apihelper import ApiException
from config import MINIGAME_TOKEN

bot = telebot.TeleBot(MINIGAME_TOKEN)

saveF = defaultdict(dict)
saveV = defaultdict(dict)

def send_safe(message, text):
    try:
        bot.send_message(message.chat.id, text, timeout=5)
    except ApiException as e:
        if "Too Many Requests" in str(e):
            time.sleep(5)  # Espera se exceder limite
            send_safe(message, text)

# Verificações de mensagem

def verificar_inicio(mensagem):
    if mensagem is None:
        return True

def verificar(mensagem):
    if mensagem.text == 'jogar' or mensagem.text == "/games":
        return True

def verificar_coordenada(mensagem):
    if mensagem.text[1] == ",":
        return True

def verificar_chute(mensagem):
    if len(saveF) > 0:
        return True


# Mensagens iniciais

inicio = """🤖Bem vindo ao Bot de Mini Games PVE🤖
          🕹️Escreva 'jogar' para iniciar🕹️  """
@bot.message_handler(commands=["start"])
def reponderInicio(mensagem):
    bot.send_message(mensagem.chat.id, inicio, timeout=5)


menu ="""🎮Escolha o jogo que deseja jogar🎮:
        /forca
        /velha"""
@bot.message_handler(func=verificar)
def reponderMenu(mensagem):
    bot.send_message(mensagem.chat.id, menu, timeout=5)


# Forca

@bot.message_handler(func=verificar_chute)
def chute_usuario(mensagem):
    resposta = receber_chute(mensagem)
    send_safe(mensagem, resposta)
    # bot.send_message(mensagem.chat.id, resposta, timeout=5)


opcoes_senhas = ['python', 'assembly', 'github', 'programaçao', 'Alan Turing', 'estagiario', 'desenvolvedor', 'javascript', 'telegram', ]
@bot.message_handler(commands=["forca"])
def jogarForca(mensagem):
    chat_id = mensagem.chat.id
    senha = opcoes_senhas[random.randrange(len(opcoes_senhas))]
    saveF.pop(chat_id, print('Save não encontrado'))
    
    saveF[chat_id] = {
        'senha': senha,
        'acertadas': '',
        'erros': 0,
        'senha_oculta': '_' * len(senha)
    }
    saveF[chat_id]['erros'] = 0
    bot.send_message(chat_id, (
        "Bem-vindo ao jogo da forca!\n"
        f"Senha: {saveF[chat_id]['senha_oculta']}\n"
        "Digite uma letra para começar."
        ),
        timeout=5
        )

def receber_chute(mensagem):
        chat_id = mensagem.chat.id
        chute = mensagem.text.strip().lower()

        if chat_id not in saveF:
            bot.send_message(chat_id, "Digite /forca para iniciar um novo jogo.", timeout=5)
            return

        saveF_atual = saveF[chat_id]

        if len(chute) != 1 or not chute.isalpha():
            bot.send_message(chat_id, "Por favor, digite apenas uma letra.", timeout=5)

        if chute in saveF_atual['acertadas']:
            bot.send_message(chat_id, "Você já chutou essa letra. Tente outra.", timeout=5)

        if chute in saveF_atual['senha']:
            saveF_atual['acertadas'] += chute
            resposta = f"'{chute}' está na senha!\n"
            resposta += desenhar_forca(saveF_atual['erros'])
        else:
            saveF_atual['erros'] += 1
            resposta = f"'{chute}' não está na senha. Erros: {saveF_atual['erros']}/6\n"
            resposta += desenhar_forca(saveF_atual['erros'])

        senha_oculta = ''
        for letra in saveF_atual['senha']:
            if letra in saveF_atual['acertadas']:
                senha_oculta += letra
            else:
                senha_oculta += '_'
        saveF_atual['senha_oculta'] = senha_oculta

        resposta += f"Senha: {senha_oculta}"

        if saveF_atual['senha_oculta'] == saveF_atual['senha']:
            resposta += "\nParabéns! Você acertou a senha secreta."
            saveF.pop(chat_id, print('Save não encontrado'))
        elif saveF_atual['erros'] == 6:
            resposta += f"\nVocê perdeu. A senha era: {saveF_atual['senha']}"
            saveF.pop(chat_id, print('Save não encontrado')) 
        return resposta

def desenhar_forca(erros):
        partes = [
            '-------------\n|\n|\n|\n|\n|\n',
            '-------------\n|           O\n|\n|\n|\n|\n|\n',
            '-------------\n|           O\n|            I\n|\n|\n|\n',
            '-------------\n|           O\n|           ´I\n|\n|\n|\n',
            '-------------\n|           O\n|           ´I`\n|\n|\n|\n',
            '-------------\n|           O\n|           ´I`\n|           ´\n|\n|\n',
            '-------------\n|           O\n|           ´I`\n|           ´ `\n|\n|\n'
        ]
        return partes[erros]


# Jogo da Velha

jogo = [
    ["" , "" , ""],
    ["" , "" , ""],
    ["" , "" , ""]
]


def exibirJogo(jogo):
    tabuleiro = ""
    for i in range(3):
        linha = ""
        for j in range(3):
            valor = jogo[i][j] if jogo[i][j] else " - "
            linha += valor
            if j < 2:
                linha += "  |" if valor == " " else "|"
        tabuleiro += linha + "\n" 
    return tabuleiro


def zerarJogo(jogo, listaX, listaO):
    for i in range(3):
        for j in range(3):
            jogo[i][j] = ""
            
    listaX.clear()
    listaO.clear()


@bot.message_handler(commands=["velha"])
def jogarVelha(mensagem):
    chat_id = mensagem.chat.id
    inicio = exibirJogo(jogo)

    send_safe(mensagem,
        "===Bem-vindo ao jogo da velha!===\n" +
        "Escreva onde desejar jogar(linha, coluna):\n" +
        f"{inicio}"
        )
    
    # bot.send_message(chat_id, (
    #     "===Bem-vindo ao jogo da velha!===\n" +
    #     "Escreva onde desejar jogar(linha, coluna):\n" +
    #     f"{inicio}"
    #     ),
    #     timeout=5
    #     )


@bot.message_handler(func=verificar_coordenada)
def marcarUsuario(mensagem):
    if not verificar_coordenada(mensagem):
        return

    chat_id = mensagem.chat.id
    deuVelha(chat_id)
    coordenada = mensagem.text.strip(",")
    linha = int(coordenada[0])
    coluna = int(coordenada[2])
    if getPosicao(linha, coluna) == "X" or getPosicao(linha, coluna) == "O":
        send_safe(mensagem, "Casa ocupada, joque novamente")
        # bot.send_message(chat_id, "Casa ocupada, jogue novamente.", timeout=5)
        return
    else:
        jogo[linha-1][coluna-1] = "X"

    send_safe(mensagem, exibirJogo(jogo))
    # bot.send_message(chat_id, exibirJogo(jogo), timeout=5)

    if xVenceu():
        zerarJogo(jogo, listaX, listaO)
        send_safe(mensagem, "Parabéns, você venceu!")
        # bot.send_message(chat_id, "Parabéns, você venceu!", timeout=5)
    else: 
        marcarBot(chat_id)


def marcarBot(chat_id):
    deuVelha(chat_id)
    linha = random.randrange(3)
    coluna = random.randrange(3)
    if getPosicao(linha, coluna) == "X" or getPosicao(linha, coluna) == "O":
        marcarBot(chat_id)
    else:
        jogo[linha-1][coluna-1] = "O"
        texto = exibirJogo(jogo)
        bot.send_message(chat_id, texto, timeout=5)

    if oVenceu():
        zerarJogo(jogo, listaX, listaO)
        bot.send_message(chat_id, "Você perdeu, tente novamente.", timeout=5)


def getPosicao(linha, coluna):
    return jogo[linha-1][coluna-1]


listaX = []
listaO = []
venceu = [
    [[1,1], [1,2], [1,3]],
    [[2,1], [2,2], [2,3]],
    [[3,1], [3,2], [3,3]],
    [[1,1], [2,1], [3,1]],
    [[1,2], [2,2], [2,3]],
    [[1,3], [2,3], [3,3]],
    [[1,1], [2,2], [3,3]],
    [[1,3], [2,2], [3,1]]
]
def xVenceu():
    for i in range(1,4):
        for j in range(1,4):
            if getPosicao(i,j) == "X":
                listaX.append([i,j])

    for combinacao in venceu:
        x_ganhou = True
        for pos in combinacao:
            if pos not in listaX:
                x_ganhou = False
                break
        if x_ganhou:
            return True
        
        
def oVenceu():
    for i in range(1,4):
        for j in range(1,4):
            if getPosicao(i,j) == "O":
                listaO.append([i,j])

    for combinacao in venceu:
        o_ganhou = True
        for pos in combinacao:
            if pos not in listaO:
                o_ganhou = False
                break
        if o_ganhou:
            return True


def deuVelha(chat_id):
    casas_vazias = 0
    for linha in jogo:
        for casa in linha:
            if casa != "X" and casa != "O":
                casas_vazias += 1
    if casas_vazias == 0:
        bot.send_message(chat_id, "Deu velha, ninguém ganhou.", timeout=5)
        zerarJogo(jogo, listaX, listaO)

bot.polling()