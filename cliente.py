import socket as sock
import threading as th

#AQUI COLOCA-SE O IP DO SERVIDOR A SE CONECTAR
HOST = "127.0.0.1"      #  <-- IP DO SERVIDOR
PORTA = 9999            #  <-- PORTA UTILIZADA

socket_cliente = sock.socket(sock.AF_INET, sock.SOCK_STREAM)

#CLIENTE SOLOCITA CONEXÃO
socket_cliente.connect((HOST,PORTA))
print(5*"*"+"Chat Iniciado"+5*"*")
print(f"\nLISTA DE COMANDOS:\n- /sair : Desconecta do chat\n\n- pv/(nomeDoUsuario) : Envia a mensagem somente para o usuário informado\n--- Exemplo: pv/rodrigo Oi, rô! Só você pode ler isso!\n")
# Loop para envio do Username
while True:
    nome = input("Informe seu nome: ")
    socket_cliente.sendall(nome.encode())

    resposta = socket_cliente.recv(1024).decode()
    if resposta == "Nome já em uso. Tente outro.":
        print(resposta)
    else:
        print(resposta)
        break

# Thread de recebimento de mensagem 
def recebe_mensagem():
    while True:
        try:
            mensagem = socket_cliente.recv(1024).decode()
            if mensagem:
                if not mensagem.startswith(f"\n{nome} >>>"):
                    print(mensagem)
            else:
                raise Exception("Conexão fechada pelo servidor.")
        except:
            print("Desconectado do chat.")
            socket_cliente.close()
            break


thread_receber = th.Thread(target=recebe_mensagem)
thread_receber.start()

#CLIENTE ENVIA DADOS PARA O SERVIDOR
while True:
    try:
        mensagem = input('')
        if mensagem == '/sair' :
            socket_cliente.close()
        else:
            socket_cliente.sendall(mensagem.encode())
    except:
        socket_cliente.close()
        break