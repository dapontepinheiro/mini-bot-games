import telebot, random, time
from collections import defaultdict
from telebot.apihelper import ApiException
import os

MINIGAME_TOKEN = os.environ["MINIGAME_TOKEN"]

bot = telebot.TeleBot(MINIGAME_TOKEN)

def send_safe(message, text):
    try:
        bot.send_message(message.chat.id, text, timeout=5)
    except ApiException as e:
        if "Too Many Requests" in str(e):
            time.sleep(10)
            send_safe(message, text)

save_forca = defaultdict(dict)
save_velha = defaultdict(dict)
save_batalha = defaultdict(dict)


# Verificações de mensagem

def verificar_casa(mensagem):
    if len(save_velha[mensagem.chat.id]) > 0:
        return True


def verificar_chute(mensagem):
    if len(save_forca[mensagem.chat.id]) > 0:
        return True
    
def verificar_preencher(mensagem):
    if len(save_batalha) > 0:
        if save_batalha[mensagem.chat.id]["Estado"] == "Aguardando jogo":
            return True
    return False

def verificar_ataque(mensagem):
    if len(save_batalha) > 0:
        if save_batalha[mensagem.chat.id]['Estado'] == "Atacando":
            return True
    return False

# Mensagens iniciais

menu ="""🤖Bem vindo ao Bot de Mini Games PVE🤖
🕹️Escolha o jogo que deseja jogar🕹️:
/forca
/velha
/batalha"""
@bot.message_handler(commands=["start"])
def reponder_menu(mensagem):
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


opcoes_senhas = ['codificar', 'assembly', 'segredo', 'programaçao', 'Alan Turing', 'estagiario', 'desenvolvedor', 'telegram']
@bot.message_handler(commands=["forca"])
def jogar_forca(mensagem):
    chat_id = mensagem.chat.id
    senha = opcoes_senhas[random.randrange(len(opcoes_senhas))]
    save_forca.clear()
    save_velha.clear()
    save_batalha.celar()
    lista_chutes.clear()

    save_forca[chat_id] = {
        'senha': senha,
        'acertadas': '',
        'erros': 0,
        'senha_oculta': '_' * len(senha)
    }

    send_safe(mensagem, (
        "Bem-vindo ao jogo da forca!\n"
        f"Senha: {save_forca[chat_id]['senha_oculta']}\n"
        "Digite uma letra para começar."
        ))


def receber_chute(mensagem, chute):
        chat_id = mensagem.chat.id

        if chat_id not in save_forca:
            send_safe(mensagem, "Digite /forca para iniciar um novo jogo.")
            return

        saveF_atual = save_forca[chat_id]

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
            save_forca.clear()

        elif saveF_atual['erros'] == 6:
            resposta += f"\nVocê perdeu. A senha era: {saveF_atual['senha']}"
            save_forca.clear()

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


def exibir_jogo(jogo):
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
def jogar_velha(mensagem):
    chat_id = mensagem.chat.id
    inicio = exibir_jogo(jogo)
    save_velha.clear()
    save_forca.clear()
    save_batalha.clear()

    send_safe(mensagem,
        "===Bem-vindo ao jogo da velha!===\n" +
        "Escolha onde desejar jogar(linha, coluna):\n"
        f"{inicio}"
        )
    
    save_velha[chat_id] = {
        'jogando': 1
    }


@bot.message_handler(func=verificar_casa)
def marcar_usuario(mensagem):
    try:
        coordenada = mensagem.text.replace(",", "")

        chat_id = mensagem.chat.id
        if deuVelha(chat_id):
            return
        linha = int(coordenada[0])
        coluna = int(coordenada[1])
        if get_posicao(linha, coluna) == "X" or get_posicao(linha, coluna) == "O":
            send_safe(mensagem, "Casa ocupada, joque novamente")
            return
        else:
            jogo[linha-1][coluna-1] = "X"

        send_safe(mensagem, exibir_jogo(jogo))

        if xVenceu():
            zerarJogo(jogo, listaX, listaO)
            send_safe(mensagem, "Parabéns, você venceu!\nUse /velha para jogar novamente.")
        else:
            if deuVelha(chat_id) == False:
                marcar_bot(mensagem)
        
    except ValueError:
        send_safe(mensagem, "As linhas e colunas devem ser números, tente novamente.")
    except IndexError:
        send_safe(mensagem, "Linha ou coluna inexistentes, tente novamente.")


def marcar_bot(mensagem):
    chat_id = mensagem.chat.id
    deuVelha(chat_id)
    linha = random.randrange(3)
    coluna = random.randrange(3)
    if get_posicao(linha, coluna) == "X" or get_posicao(linha, coluna) == "O":
        marcar_bot(mensagem)
    else:
        jogo[linha-1][coluna-1] = "O"
        texto = exibir_jogo(jogo)
        send_safe(mensagem, texto)

    if oVenceu():
        zerarJogo(jogo, listaX, listaO)
        send_safe(mensagem, "Você perdeu.\nUse /velha para jogar novamente")


def get_posicao(linha, coluna):
    return jogo[linha-1][coluna-1]


def xVenceu():
    for i in range(1,4):
        for j in range(1,4):
            if get_posicao(i,j) == "X":
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
            if get_posicao(i,j) == "O":
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


# Batalha Naval

campo_usuario = [
    ["" for _ in range(8)] for _ in range(8)
    ]
campo_inimigo = [
    ["" for _ in range(8)] for _ in range(8)
    ]

navios_usuario = []
atingidos_usuario = []
ataques_usuario = []

navios_inimigo = []
atingidos_inimigo = []
ataques_inimigo = []

navios = {
    1: "Destroyer",
    2: "Submarino",
    3: "Navio de Batalha",
    4: "Porta Aviões"
}

tamanho_navios = {
    "Destroyer": 2,
    "Submarino": 3,
    "Navio de Batalha": 4,
    "Porta Aviões" : 5
}

def exibir_pecas(chat_id):
    pecas_txt = ""

    for navio in navios:
        if navio not in save_batalha[chat_id]['Peças jogadas']:
            pecas_txt += f"{str(navio)}. "
            pecas_txt += navios[navio]
            pecas_txt += " (tamanho: " + str(tamanho_navios[navios[navio]]) + ")" + "\n"

    return pecas_txt


def exibir_tabuleiro(campo):
    tabuleiro = "  1  2  3  4  5  6  7  8\n"
    letras = ['A','B','C','D','E','F','G', 'H']
    for i in range(8):
        linha = ""
        linha += letras[i]
        for j in range(8):
            if campo[i][j] in ["D","S","N","P"]:
                valor = " " + campo[i][j] + " "
            elif campo[i][j]:
                valor = campo[i][j]
            else:
                valor = " - "
            linha += valor
        tabuleiro += linha + "\n" 
    return tabuleiro


def tabuleiro_inimigo():
    tabuleiro = "  1  2  3  4  5  6  7  8\n"
    letras = ['A','B','C','D','E','F','G','H']

    for i in range(8):
        linha = ""
        linha += letras[i]
        for j in range(8):
            valor = " - " if campo_inimigo[i][j] in ["D","S","N","P",""] else f"{campo_inimigo[i][j]}"
            linha += valor
        tabuleiro += linha + "\n" 
    return tabuleiro


def posicao_valida(linha, coluna, tamanho, direcao, campo):
    if direcao == "H":
        if coluna + tamanho > 8:
            return False
        for c in range(coluna, coluna + tamanho):
            if campo[linha][c] != "":
                return False
    else:
        if linha + tamanho > 8:
            return False
        for l in range(linha, linha + tamanho):
            if campo[l][coluna] != "":
                return False
    return True


@bot.message_handler(commands=['batalha'])
def jogar_batalha_naval(mensagem):
    chat_id = mensagem.chat.id
    save_batalha.clear()
    save_batalha[chat_id] = {
        "Peças jogadas": [],
        "Jogadas": [],
        "Estado": "Aguardando jogo"
    }

    send_safe(mensagem, """⚓⚔Se prepare, a Batalha Naval vai começar!⚓⚔
                     Preencha seu tabuleiro:""")
    bot.send_message(chat_id, f"\nTabuleiro do Usuário\n`{exibir_tabuleiro(campo_usuario)}`", parse_mode='MarkdownV2')

    send_safe(mensagem, f"{exibir_pecas(chat_id)}\nEscolha a peça, coordenada e direção(H ou V) em que deseja jogar(ex: '3 A1 H'):")


pecas = [1, 2, 3, 4]
linhas = {
    'A': 0,
    'B': 1,
    'C': 2,
    'D': 3,
    'E': 4,
    'F': 5,
    'G': 6,
    'H': 7
}
colunas = [0, 1, 2, 3, 4, 5, 6, 7]
direcoes = ['H', 'V']
@bot.message_handler(func=verificar_preencher)
def preencher_tabuleiro(mensagem):
    chat_id = mensagem.chat.id
    save_atual = save_batalha[chat_id]

    try:
        partes = mensagem.text.split()
        if len(partes) != 3:
            raise ReferenceError
        
        peca, coordenada, direcao = partes
        peca = int(peca)
        linha = coordenada[0].upper()
        coluna = int(coordenada[1]) - 1
        direcao = direcao.upper()

        if peca not in pecas or linha not in linhas or coluna not in colunas or direcao not in direcoes:
            raise ValueError
        if peca in save_atual["Peças jogadas"]:
            raise NameError
        
        linha = linhas[linha]
        navio = navios[peca]
        tamanho = tamanho_navios[navio]

        if posicao_valida(linha, coluna, tamanho, direcao, campo_usuario):
            if direcao == "H":
                for c in range(coluna, coluna + tamanho):
                    campo_usuario[linha][c] = navio[0]
                    navios_usuario.append([linha, c])
            else:
                for l in range(linha, linha + tamanho):
                    campo_usuario[l][coluna] = navio[0] 
                    navios_usuario.append([l, coluna])   
        else:
            raise IndexError

        save_atual['Peças jogadas'].append(peca) 
    
        if len(save_atual['Peças jogadas']) < 4:
            bot.send_message(chat_id, f"`{exibir_tabuleiro(campo_usuario)}`\nJogada registrada\! Faltam {4 - len(save_atual['Peças jogadas'])} jogadas\.", parse_mode='MarkdownV2')
            send_safe(mensagem, f"{exibir_pecas(chat_id)}\nPreencha com a próxima peça:")
        else:
            preencher_tabuleiro_inimigo()
            bot.send_message(chat_id, f"`{exibir_tabuleiro(campo_usuario)}`", parse_mode='MarkdownV2')
            send_safe(mensagem, "Tabuleiro preenchido, vamos começar o jogo!")
            save_batalha[chat_id]['Estado'] = "Atacando"
            send_safe(mensagem, "Escolha aonde deseja atacar(ex: 'A4'): ")

    except ValueError:
        send_safe(mensagem, "Peça, coordenada ou direção invalidás, tente novamente: ")
    except ReferenceError:
        send_safe(mensagem, "Entrada inválida, use o formato peça coordenada direção(H ou V) (ex: '3 A1 H): ")
    except IndexError:
        send_safe(mensagem, "Posição inválida, tente novamente: ")
    except NameError:
        send_safe(mensagem, "Peça já jogada, tente novamente: ")


def preencher_tabuleiro_inimigo():
    pecas_jogadas = []
    while len(pecas_jogadas) < 4:
        linha = random.randint(0,7)
        coluna = random.randint(0,7)
        navio = navios[random.randint(1,4)]
        tamanho = tamanho_navios[navio]
        direcao = random.choice(["H", "V"])

        if navio in pecas_jogadas:
            continue

        if posicao_valida(linha, coluna, tamanho, direcao, campo_inimigo):
            if direcao == "H":
                for c in range(coluna, coluna + tamanho):
                    campo_inimigo[linha][c] = navio[0] 
                    navios_inimigo.append([linha, c])
            else:
                for l in range(linha, linha + tamanho):
                    campo_inimigo[l][coluna] = navio[0]    
                    navios_inimigo.append([l, coluna])   

            pecas_jogadas.append(navio)


@bot.message_handler(func=verificar_ataque)
def ataque(mensagem):
    try:
        linha = linhas[mensagem.text[0].upper()]
        coluna = int(mensagem.text[1]) - 1
        if linha < 0 or linha > 7 or coluna < 0 or coluna > 7:
            raise ValueError
        
        if [linha,coluna] in ataques_usuario:
            raise RuntimeError
        else:
            if campo_inimigo[linha][coluna] in ["D", "S", "N", "P"]:
                send_safe(mensagem, f"Você acertou um barco! 💥")
                atingidos_inimigo.append(campo_inimigo[linha][coluna])
                navios_inimigo.remove([linha, coluna])
                campo_inimigo[linha][coluna] = " 💥"
            else:
                send_safe(mensagem, f"Você acertou a água 💦")
                campo_inimigo[linha][coluna] = " X "
            
            ataques_usuario.append([linha, coluna])
            ataque_inimigo(mensagem)
    except ValueError or IndexError or KeyError:
        send_safe(mensagem, "Linha ou coluna inexistente, tente novamente.")
    except RuntimeError:
        send_safe(mensagem, "Você já atacou esse local, tente um outro.")


def ataque_inimigo(mensagem):
    chat_id = mensagem.chat.id
    linha = random.randint(0,7)
    coluna = random.randint(0,7)
    
    if campo_usuario[linha][coluna] in ["D", "S", "N", "P"]:
        send_safe(mensagem, "Um barco foi atingido pelo inimigo 💥")
        atingidos_usuario.append(campo_usuario[linha][coluna])
        navios_usuario.remove([linha, coluna])
        campo_usuario[linha][coluna] = " 💥"
    else:
        send_safe(mensagem, "O inimigo atingiu a água 💦")
        campo_usuario[linha][coluna] = " X "    
    
    ataques_inimigo.append([linha, coluna])
    barcos_atingidos()
    if venceuBatalha():
        send_safe(mensagem, "Você venceu! Use /batalha para jogar novamente.")
        save_batalha.clear()
    elif perdeuBatalha():
        send_safe(mensagem, "Você perdeu. Use /batalha para jogar novamente.")
        save_batalha.clear()
    else:    
        bot.send_message(chat_id, f"""
                Tabuleiro Inimigo\n`{tabuleiro_inimigo()}`
    \=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=        
            Tabuleiro do Usuário\n`{exibir_tabuleiro(campo_usuario)}`""", parse_mode='MarkdownV2')
    

def barcos_atingidos():
    quant_DU, quant_SU, quant_NU, quant_PU, quant_DI, quant_SI, quant_NI, quant_PI = 0,0,0,0,0,0,0,0

    for i in atingidos_usuario:
        if i == "D":
            quant_DU +=1
        elif i == "S":
            quant_SU += 1
        elif i == "N":
            quant_NU += 1
        elif i == "P":
            quant_PU += 1

    for i in atingidos_inimigo:
        if i == "D":
            quant_DI +=1
        elif i == "S":
            quant_SI += 1
        elif i == "N":
            quant_NI += 1
        elif i == "P":
            quant_PI += 1

    try:
        if quant_DU == 2:
            print("Um de seus barcos foi afundado!")
            atingidos_usuario.remove("D")
        elif quant_SU == 3:
            print("Um de seus barcos foi afundado!")
            atingidos_usuario.remove("S")   
        elif quant_NU == 4:
            print("Um de seus barcos foi afundado!")
            atingidos_usuario.remove("N")
        elif quant_PU == 5:
            print("Um de seus barcos foi afundado!")
            atingidos_usuario.remove("P")

        if quant_DI == 2:
            print("Você afundou um barco!")
            atingidos_inimigo.remove("D")
        elif quant_SI == 3:
            print("Você afundou um barco!")
            atingidos_inimigo.remove("S")   
        elif quant_NI == 4:
            print("Você afundou um barco!")
            atingidos_inimigo.remove("N")
        elif quant_PI == 5:
            print("Você afundou um barco!")
            atingidos_inimigo.remove("P")

    except:
        ...


def venceuBatalha():
    if len(navios_inimigo) == 0:
        return True
    else:
        return False


def perdeuBatalha():
    if len(navios_usuario) == 0:
        return True
    else:
        return False


bot.polling()
