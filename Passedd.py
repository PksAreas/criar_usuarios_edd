from netmiko import ConnectHandler
from netmiko import NetMikoTimeoutException
from netmiko import exceptions
from getpass import getpass
import tkinter as tk

def consulta():
    user = input('Enter your username: ')
    password = getpass(prompt='Enter your password: ')
        
    pass_type = int(input('''Type of password [0 or 7]
0  Specify password in plain text
7  Specify password in encrypted form
Enter the type of password: '''))

    new_user = input('enter the user to be searched: ')
    new_pass = input('enter the new password: ')

    access_level = int(input('enter the access level [0...15] : '))

    with open('ip.txt','r') as file:
        ips = file.read()
    
    for ip in ips.split():
        edd = {
            'device_type': 'cisco_ios',
            'ip': ip,
            'username': user,
            'password': password
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
                    print('Usuario encontrado. Deseja Alterar a senha?')
                    resposta = input('Digite y(sim) ou n(não): ')
                    match resposta:
                        case 'y':
                            print('Alterando senha...')
                            try: 
                                net_connect.send_command_timing('config')
                                net_connect.send_command_timing(f'username {new_user} access-level {access_level}')
                                net_connect.send_command_timing(f'username {new_user} password {pass_type} {new_pass}')
                                print('Senha alterada com sucesso!')
                            except Exception as e:
                                print(f'Erro: {e}')
                        case 'n':
                            print('Nada foi alterado.')
                else:
                    print('Usuario não encontrado.')
                    print('Deseja criar o usuario?')
                    resposta = input('Digite y(sim) ou n(não): ')
                    match resposta:
                        case 'y':
                            print('Criando usuario...')
                            try: 
                                net_connect.send_command_timing('config')
                                net_connect.send_command_timing(f'username {new_user} access-level {access_level}')
                                net_connect.send_command_timing(f'username {new_user} password {pass_type} {new_pass}')
                                print('Usuario criado com sucesso!')    
                            except Exception as e:
                                print(f'Erro: {e}')
                        case 'n':
                            print('Nada foi alterado.')
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
        print(username,password,newuser,newpass,passwdtype,accesslevel)

    #Configuração da janela
    janela = tk.Tk()
    janela.title('EDD')
    janela.geometry('300x200')

    #Configuração dos widgets (Caixa de texto e botões)
    label_user = tk.Label(janela, text='User')
    user = tk.Entry(janela)
    label_passwd = tk.Label(janela, text='Password')
    passwd = tk.Entry(janela, show='*')
    new_user_label = tk.Label(janela, text='New User')
    new_user = tk.Entry(janela)
    new_pass_label = tk.Label(janela, text='New Password')
    new_pass = tk.Entry(janela)
    access_level_label = tk.Label(janela, text='Access Level')
    access_level = tk.Entry(janela)
    passwd_type_label = tk.Label(janela, text='Password Type')
    passwd_type = tk.Entry(janela)

    #Botão de enviar
    botão_enviar = tk.Button(janela,text='Enviar',command=enviar)

    #Pack dos widgets
    label_user.pack()
    user.pack()
    label_passwd.pack()
    passwd.pack()
    new_user_label.pack()
    new_user.pack()
    new_pass_label.pack()
    new_pass.pack()
    access_level_label.pack()
    access_level.pack()
    passwd_type_label.pack()
    passwd_type.pack()
    botão_enviar.pack()

    #Inicia a janela
    janela.mainloop()

interface()
