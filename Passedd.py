from netmiko import ConnectHandler
from netmiko import NetMikoTimeoutException
from netmiko import exceptions
import tkinter as tk
from tkinter import ttk

import tkinter as tk

def pop_up(texto: str) -> str:

    def yes():
        nonlocal resposta
        resposta = 'y'
        windows.destroy()

    def no():
        nonlocal resposta
        resposta = 'n'
        windows.destroy()

    # Criação da janela
    windows = tk.Toplevel()
    windows.title('Aviso')
    windows.geometry('300x100')
    windows.resizable(False, False)  # Impede redimensionamento

    # Widgets da janela
    label = tk.Label(windows, text=texto, font=("Arial", 12), wraplength=280)
    botao_yes = tk.Button(windows, text='YES', command=yes, width=10, bg='green', fg='white')
    botao_no = tk.Button(windows, text='NO', command=no, width=10, bg='red', fg='white')

    # Layout dos widgets
    label.pack(pady=10)
    botao_yes.pack(side=tk.LEFT, padx=20, pady=10)
    botao_no.pack(side=tk.RIGHT, padx=20, pady=10)

    # Variável de resposta
    resposta = 'none'

    # Inicia o loop da janela
    windows.grab_set()  # Impede interação com a janela principal
    windows.wait_window()  # Aguarda o fechamento da janela
    print (resposta)
    return resposta


def consulta(user,password,new_user,new_pass,passwd_type,access_level):   
    with open('ip.txt','r') as file:
        ips = file.read()
    
    for ip in ips.split():
        edd = {
            'device_type': 'cisco_ios',
            'ip': ip,
            'username': user,
            'password': password,
            'session_log': 'log.txt'
        }
        
        try:
            net_connect = ConnectHandler(**edd)
            net_connect.find_prompt()

            try:
                usuarios = net_connect.send_command(f'show running-config | include {new_user} password').splitlines()[1]
            except:
                usuarios = (' ')

            for i in usuarios.splitlines():
                if new_user in i:
                    
                    texto = 'Usuario encontrado. Deseja Alterar a senha?'
                    resposta = str(pop_up(texto))
                    print (resposta)

                    match resposta:
                        case 'y':
                            print('Alterando senha...')
                            try: 
                                net_connect.send_command_timing('config')
                                net_connect.send_command_timing(f'username {new_user} access-level {access_level}')
                                net_connect.send_command_timing(f'username {new_user} password {passwd_type} {new_pass}')
                                print('Senha alterada com sucesso!')
                                net_connect.disconnect()
                            except Exception as e:
                                print(f'Erro: {e}')
                                net_connect.disconnect()
                            continue
                        case 'n':
                            print('Nada foi alterado.')
                            net_connect.disconnect()
                            continue
                else:

                    texto = 'Usuario não encontrado. Deseja criar o usuario?'
                    resposta = pop_up(texto)
                    print (resposta)
                    
                    match resposta:
                        case 'y':
                            print('Criando usuario...')
                            try: 
                                net_connect.send_command_timing('config')
                                net_connect.send_command_timing(f'username {new_user} access-level {access_level}')
                                net_connect.send_command_timing(f'username {new_user} password {passwd_type} {new_pass}')
                                print('Usuario criado com sucesso!')
                                net_connect.disconnect()
                            except Exception as e:
                                print(f'Erro: {e}')
                                net_connect.disconnect()
                            continue
                        case 'n':
                            print('Nada foi alterado.')
                            net_connect.disconnect()
                            
                            continue
        except NetMikoTimeoutException:
            print(f'Erro de conexão com o dispositivo {ip}')
        except exceptions.ReadTimeout:
            print(f'O dispositivo {ip} demorou para responder')

def interface():

    def enviar():
        username = user.get()
        password = passwd.get()
        newuser = new_user.get()
        newpass = new_pass.get()
        accesslevel = access_level.get()
        passwdtype = passwd_type.get()
        consulta(username,password,newuser,newpass,passwdtype,accesslevel)

    #Configuração da janela
    janela = tk.Tk()
    janela.title('EDD')
    janela.geometry('200x300')

    #Configuração dos widgets (Caixa de texto e botões)
    label_user = tk.Label(janela, text='User')
    user = tk.Entry(janela)
    label_passwd = tk.Label(janela, text='Password')
    passwd = tk.Entry(janela, show='*')
    new_user_label = tk.Label(janela, text='New User')
    new_user = tk.Entry(janela)
    new_pass_label = tk.Label(janela, text='New Password')
    new_pass = tk.Entry(janela)

    #"Drop Menu"
    level = ['0','15']
    type = ['0','7']
    access_level_label = tk.Label(janela, text='Access Level')
    access_level = ttk.Combobox(janela, values=level,width=2)
    passwd_type_label = tk.Label(janela, text='Password Type')
    passwd_type = ttk.Combobox(janela, values=type,width=2)

    #Botão de enviar
    botão_enviar = tk.Button(janela,text='Enviar',command=enviar)

    #Pack dos widgets
    label_user.pack()
    user.pack()
    label_passwd.pack()
    passwd.pack()
    new_user_label.pack()
    new_user.pack(pady=0)
    new_pass_label.pack()
    new_pass.pack()
    passwd_type_label.pack()
    passwd_type.pack()
    access_level_label.pack()
    access_level.pack()
    botão_enviar.pack(pady=15)

    #Inicia a janela
    janela.mainloop()

interface()