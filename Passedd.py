from netmiko import ConnectHandler
from netmiko import NetMikoTimeoutException
from netmiko import exceptions
import tkinter as tk
from tkinter import ttk

def pop_up(texto,ip):

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
    windows.title(ip)
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
    return resposta

def pop_up_notify(texto,ip):
    windows = tk.Toplevel()
    windows.title(ip)
    #windows.geometry('300x100')
    #windows.resizable(False, False)  # Impede redimensionamento
    
    label = tk.Label(windows,text=texto)
    label.pack(pady=10)
    ok = tk.Button(windows, text='OK', command=windows.destroy, width=10, bg='green', fg='white')
    ok.pack(pady=10)

    windows.grab_set()  # Impede interação com a janela principal
    windows.wait_window()  # Aguarda o fechamento da janela
    return None

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
                    resposta = str(pop_up(texto,ip))

                    match resposta:
                        case 'y':
                            try: 
                                net_connect.send_command_timing('config')
                                net_connect.send_command_timing(f'username {new_user} access-level {access_level}')
                                net_connect.send_command_timing(f'username {new_user} password {passwd_type} {new_pass}')
                                net_connect.disconnect()
                                pop_up_notify('Senha alterada com sucesso!',ip)
                            except Exception as e:
                                net_connect.disconnect()
                                pop_up_notify(f'Erro ao alterar a senha!:{e}',ip)
                            continue
                        case 'n':
                            net_connect.disconnect()
                            pop_up_notify('Operação cancelada!',ip)
                            continue
                else:

                    texto = 'Usuario não encontrado. Deseja criar o usuario?'
                    resposta = pop_up(texto,ip)

                    match resposta:
                        case 'y':
                            try: 
                                net_connect.send_command_timing('config')
                                net_connect.send_command_timing(f'username {new_user} access-level {access_level}')
                                net_connect.send_command_timing(f'username {new_user} password {passwd_type} {new_pass}')
                                net_connect.disconnect()
                                pop_up_notify('Usuario criado com sucesso!',ip)
                            except Exception as e:
                                net_connect.disconnect()
                                pop_up_notify(f'Erro ao criar o usuario!:{e}',ip)
                            continue
                        case 'n':
                            net_connect.disconnect()
                            pop_up_notify('Operação cancelada!',ip)
                            continue

        except NetMikoTimeoutException:
            pop_up_notify(f'Erro de conexão com o dispositivo {ip}',ip)
        except exceptions.ReadTimeout:
            pop_up_notify(f'O dispositivo {ip} demorou para responder',ip)
        except exceptions.NetMikoAuthenticationException:
            pop_up_notify(f'Erro de autenticação no dispositivo {ip}',ip)
    
    pop_up_notify('Operação concluída!','FIM')

def criar_user_gui():

    def enviar():
        username = user.get()
        password = passwd.get()
        newuser = new_user.get()
        newpass = new_pass.get()
        accesslevel = access_level.get()
        passwdtype = passwd_type.get()
        consulta(username,password,newuser,newpass,passwdtype,accesslevel)

    #Configuração da janela
    windows = tk.Toplevel()
    windows.title('EDD')
    windows.geometry('200x300')
    windows.resizable(False, False)  # Impede redimensionamento

    #Configuração dos widgets (Caixa de texto e botões)
    label_user = tk.Label(windows, text='User')
    user = tk.Entry(windows)
    label_passwd = tk.Label(windows, text='Password')
    passwd = tk.Entry(windows, show='*')
    new_user_label = tk.Label(windows, text='New User')
    new_user = tk.Entry(windows)
    new_pass_label = tk.Label(windows, text='New Password')
    new_pass = tk.Entry(windows)

    #"Drop Menu"
    level = ['0','15']
    type = ['0','7']
    access_level_label = tk.Label(windows, text='Access Level')
    access_level = ttk.Combobox(windows, values=level,width=2)
    passwd_type_label = tk.Label(windows, text='Password Type')
    passwd_type = ttk.Combobox(windows, values=type,width=2)

    #Botão de enviar
    botão_enviar = tk.Button(windows,text='Enviar',command=enviar)

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
    windows.grab_set()  # Impede interação com a janela principal
    windows.wait_window()  # Aguarda o fechamento da janela

def delete_user(username,password,new_user):
    with open('ip.txt','r') as file:
        ips = file.read()

    for ip in ips.split():
        edd = {
            'device_type': 'cisco_ios',
            'ip': ip,
            'username': username,
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
                    try: 
                        net_connect.send_command_timing('config')
                        net_connect.send_command_timing(f'no username {new_user}')
                        net_connect.disconnect()
                        pop_up_notify('Usuario deletado com sucesso!',ip)
                    except Exception as e:
                        net_connect.disconnect()
                        pop_up_notify(f'Erro ao deletar o usuario!:{e}',ip)
                    continue
                else:
                    pop_up_notify('Usuario não encontrado!',ip)
                    continue

        except NetMikoTimeoutException:
            pop_up_notify(f'Erro de conexão com o dispositivo {ip}',ip)
        except exceptions.ReadTimeout:
            pop_up_notify(f'O dispositivo {ip} demorou para responder',ip)
        except exceptions.NetMikoAuthenticationException:
            pop_up_notify(f'Erro de autenticação no dispositivo {ip}',ip)

def delete_user_gui():
    
    def enviar():
        username = user.get()
        password = passwd.get()
        newuser = new_user.get()
        delete_user(username,password,newuser)

    #Configuração da janela 
    windows = tk.Toplevel()
    windows.title('EDD')
    windows.geometry('200x180')
    windows.resizable(False, False)  # Impede redimensionamento

    #Configuração dos widgets (Caixa de texto e botões)
    label_user = tk.Label(windows, text='User')
    user = tk.Entry(windows)
    label_passwd = tk.Label(windows, text='Password')
    passwd = tk.Entry(windows, show='*')
    new_user_label = tk.Label(windows, text='User to delete')
    new_user = tk.Entry(windows)

    #Botão de enviar
    botão_enviar = tk.Button(windows,text='Enviar',command=enviar)
    
    #Pack dos widgets
    label_user.pack()
    user.pack()
    label_passwd.pack()
    passwd.pack()
    new_user_label.pack()
    new_user.pack(pady=0)
    botão_enviar.pack(pady=15)

    #Inicia a janela
    windows.grab_set()  # Impede interação com a janela principal
    windows.wait_window()  # Aguarda o fechamento da janela

def main():
    windows = tk.Tk()
    windows.title('EDD')
    windows.geometry('290x500')
    #janela.resizable(False, False)  # Impede redimensionamento

    #Configuração dos widgets (Caixa de texto e botões)
    label = tk.Label(windows, text='Escolha uma opção:', font=("Arial", 20), wraplength=280)
    label.pack(pady=1)
    
    criar_user = tk.Button(windows, text='Criar/Alterar Usuario', command=criar_user_gui)
    criar_user.pack()

    deletar_user = tk.Button(windows, text='Deletar Usuario', command=delete_user_gui)
    deletar_user.pack()

    windows.mainloop()

if __name__ == '__main__':
    main()