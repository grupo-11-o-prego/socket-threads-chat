import socket as sock
import threading as th

clientes = [] # Array com as conexões (utilizado para a função de Broadcast)
nomes_clientes = set() # Array com valores únicos que guarda os nomes dos clientes (evitando que nomes repetidos sejam utilizados ao mesmo tempo)
nome_conn = {} # Dicionário que conecta os nomes dos usuários com suas conexões (utilizado para a função de Unicast)

HOST = '127.0.0.1'      #  <-- IP DO SERVIDOR
PORTA = 9999            #  <-- PORTA UTILIZADA

def broadcast(mensagem):
    for conn in clientes:
        try:
            conn.sendall(mensagem.encode())
        except:
            clientes.remove(conn)

def unicast(nome, mensagem):
    conn_dest = nome_conn.get(nome)
    if conn_dest:
        try:
            conn_dest.sendall(f"\n{mensagem}\n".encode())
        except:
            print(f"Erro ao enviar mensagem privada para {nome}.")


def processar_mensagem(mensagem):
    if mensagem.startswith("pv/"):
        partes = mensagem.split(" ", 1)
        if len(partes) > 1:
            comando = partes[0]
            mensagem_pv = partes[1]

            nome = comando[3:].lower() #Remover o "pv/"

            return nome, mensagem_pv
    return None, None

# Thread de recebimento de dados será iniciada com esta função
def recebe_dados(sock_conn, ender):
    while True:
        try:
            nome = sock_conn.recv(50).decode()
            nomeLower = nome.lower()
            if nomeLower in nomes_clientes:
                sock_conn.sendall("Nome já em uso. Tente outro.".encode())
                continue

            nomes_clientes.add(nomeLower)
            nome_conn[nomeLower] = sock_conn

            sock_conn.sendall(f"Seja bem vindo ao chat, {nome}!\n".encode())
            
            print(f"Conexão com sucesso com {nome} - {ender} \n")
            broadcast(f"{nome} entrou no chat.\n")
            break  # Sai do loop após aceitar o nome

        except:
            sock_conn.close()
            return

    # LOOP DE REPASSE DE MENSAGENS
    while True:
        try:
            mensagem = sock_conn.recv(1024).decode() #<--- decode transforma os bytes do recv para strings
            if mensagem:
                if mensagem.startswith("pv/"):
                    nome_usuario, msg_pv = processar_mensagem(mensagem)
                    if nome_usuario and msg_pv:
                        unicast(nome_usuario, f"[pv:{nome}] >>> {msg_pv}")
                    else:
                        print("Erro ao enviar mensagem privada.")
                else:
                    msgFormatada = f"\n{nome} >>> {mensagem}\n"
                    broadcast(msgFormatada)
            else:
                raise Exception("Cliente desconectado")
        except:
            sock_conn.close()
            clientes.remove(sock_conn)
            nomes_clientes.remove(nomeLower)
            nome_conn.pop(nomeLower)
            broadcast(f"\n{nome} saiu do chat.\n")
            print(f"Conexão FECHADA com {nome} - {ender} \n")
            break


#CRIAÇÃO DO SOCKTET DE CONEXÃO COM O SERVIDOR
sock_server = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
#LINKAR O HOST A PORTA
sock_server.bind((HOST, PORTA))
#SERVIDOR ENTRA NO MODO ESCUTA
sock_server.listen()
print(f'O servidor {HOST}:{PORTA} está aguardando conexões...')

# Cria o LOOP PRINCIPAL para aceitar VÁRIOS clientes (com uso das threads)
while True:
    try:
        # Accept retorna o socket de conexão com o cliente, retornando-a com seu endereço.
        conn, ender = sock_server.accept()
        clientes.append(conn)
    except:
        print("Erro de conexão... tente novamente")
        continue  # <-- reinicia o loop
    threadCliente = th.Thread(target=recebe_dados,args=[conn,ender])
    threadCliente.start()