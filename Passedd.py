from netmiko import ConnectHandler
from netmiko import NetMikoTimeoutException
from netmiko import exceptions
from getpass import getpass

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
            print(f'Dispositivo demorou muito para responder: {ip}')
consulta()
