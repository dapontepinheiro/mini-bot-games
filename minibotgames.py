import telebot, random, time
from collections import defaultdict
from telebot.apihelper import ApiException
import os

MINIGAME_TOKEN = os.environ["MINIGAME_TOKEN"]

bot = telebot.TeleBot(MINIGAME_TOKEN)

saveForca = defaultdict(dict)
saveVelha = defaultdict(dict)

def send_safe(message, text):
    try:
        bot.send_message(message.chat.id, text, timeout=5)
    except ApiException as e:
        if "Too Many Requests" in str(e):
            time.sleep(5)
            send_safe(message, text)

# Verificações de mensagem

def verificar_coordenada(mensagem):
    if len(saveVelha) > 0:
        return True


def verificar_chute(mensagem):
    if len(saveForca) > 0:
        return True


# Mensagens iniciais
menu ="""🤖Bem vindo ao Bot de Mini Games PVE🤖
🕹️Escolha o jogo que deseja jogar🕹️:
/forca
/velha"""
@bot.message_handler(commands=["start"])
def reponderMenu(mensagem):
    send_safe(mensagem, menu)


# Forca
lista_chutes = []
@bot.message_handler(func=verificar_chute)
def chute_usuario(mensagem):
    chute = mensagem.text.strip().lower()

    if len(chute) != 1:
        send_safe(mensagem, "Por favor, digite apenas uma letra.")
        return 
    elif not chute.isalpha():
        send_safe(mensagem, "Por favor, digite uma letra")
        return
    elif chute in lista_chutes:
        send_safe(mensagem, "Você já chutou essa letra, tente outra.")
        return
    
    lista_chutes.append(chute)
    resposta = receber_chute(mensagem, chute)
    send_safe(mensagem, resposta)


opcoes_senhas = ['python', 'assembly', 'github', 'programaçao', 'Alan Turing', 'estagiario', 'desenvolvedor', 'telegram', ]
@bot.message_handler(commands=["forca"])
def jogarForca(mensagem):
    chat_id = mensagem.chat.id
    senha = opcoes_senhas[random.randrange(len(opcoes_senhas))]
    saveForca.clear()
    lista_chutes.clear()
    
    saveForca[chat_id] = {
        'senha': senha,
        'acertadas': '',
        'erros': 0,
        'senha_oculta': '_' * len(senha)
    }

    bot.send_message(chat_id, (
        "Bem-vindo ao jogo da forca!\n"
        f"Senha: {saveForca[chat_id]['senha_oculta']}\n"
        "Digite uma letra para começar."
        ),
        timeout=5
        )


def receber_chute(mensagem, chute):
        chat_id = mensagem.chat.id

        if chat_id not in saveForca:
            send_safe(mensagem, "Digite /forca para iniciar um novo jogo.")
            return

        saveF_atual = saveForca[chat_id]

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
            resposta += "\nParabéns, você acertou a senha secreta!\nUse /forca para iniciar um novo jogo."
            saveForca.pop(chat_id, print('Save não encontrado'))
        elif saveF_atual['erros'] == 6:
            resposta += f"\nVocê perdeu. A senha era: {saveF_atual['senha']}"
            saveForca.pop(chat_id, print('Save não encontrado')) 
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


@bot.message_handler(commands=["velha"])
def jogarVelha(mensagem):
    chat_id = mensagem.chat.id
    inicio = exibirJogo(jogo)
    saveVelha.pop(chat_id, print("Save velha não encontrado"))
    print("Save velha apagado")

    send_safe(mensagem,
        "===Bem-vindo ao jogo da velha!===\n" +
        "Escolha onde desejar jogar(linha, coluna):\n"
        f"{inicio}"
        )
    
    saveVelha[chat_id] = {
        'jogando': 1
    }
    print("Save velha criado")


@bot.message_handler(func=verificar_coordenada)
def marcarUsuario(mensagem):
    try:
        coordenada = mensagem.text.replace(",", "")

        chat_id = mensagem.chat.id
        if deuVelha(chat_id):
            return
        linha = int(coordenada[0])
        coluna = int(coordenada[1])
        if getPosicao(linha, coluna) == "X" or getPosicao(linha, coluna) == "O":
            send_safe(mensagem, "Casa ocupada, joque novamente")
            return
        else:
            jogo[linha-1][coluna-1] = "X"

        send_safe(mensagem, exibirJogo(jogo))

        if xVenceu():
            zerarJogo(jogo, listaX, listaO)
            send_safe(mensagem, "Parabéns, você venceu!\nUse /velha para jogar novamente.")
        else:
            if deuVelha(chat_id) == False:
                marcarBot(chat_id)
        
    except ValueError:
        send_safe(mensagem, "As linhas e colunas devem ser números, tente novamente.")
    except IndexError:
        send_safe(mensagem, "Linha ou coluna inexistentes, tente novamente.")


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
        bot.send_message(chat_id, "Você perdeu.\nUse /velha para jogar novamente", timeout=5)


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
        bot.send_message(chat_id, "Deu velha, ninguém ganhou.\nUse /velha para jogar novamente", timeout=5)
        zerarJogo(jogo, listaX, listaO)
        return True
    
    return False


def zerarJogo(jogo, listaX, listaO):
    for i in range(3):
        for j in range(3):
            jogo[i][j] = ""       
    listaX.clear()
    listaO.clear()

bot.polling()
