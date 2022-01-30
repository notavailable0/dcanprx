import os
import time
import digitalocean
import paramiko
import random

from io import StringIO
from Crypto.PublicKey import RSA

from multiprocessing import Pool, freeze_support

from digitalocean import SSHKey
from dopy.manager import DoManager

from db_managment import *

def list_of_active_servers(token):
    manager = digitalocean.Manager(token=token)
    my_droplets = manager.get_all_droplets()

    my_droplets_ips = []

    private_ssh_key = get_special_token(token.strip())[0][2]
    print(private_ssh_key)

    for i in my_droplets:
        my_droplets_ips.append(str(i.ip_address)+':'+str(private_ssh_key))

    return my_droplets_ips

def setup_servers(ip):
    print(ip)
    try:

            hostname = ip.split(':')[0]
            myuser   = 'root'
            mySSHK   = paramiko.RSAKey.from_private_key(StringIO(ip.split(':')[1]))

            sshcon = paramiko.SSHClient()  # will create the object
            sshcon.set_missing_host_key_policy(paramiko.AutoAddPolicy()) # no known_hosts error

            sshcon.connect(hostname, username=myuser, pkey=mySSHK) # no passwd needed

            def run_command_on_ssh_server(command, ssh=sshcon):
                stdin, stdout, stderr = ssh.exec_command(command)
                exit_status = stdout.channel.recv_exit_status()
                print(exit_status)

            run_command_on_ssh_server("sudo apt-get update;sudo apt-get install build-essential libevent-dev libssl-dev --yes;sudo wget https://github.com/z3APA3A/3proxy/archive/0.9.3.tar.gz;sudo tar -zxvf 0.9.3.tar.gz;cd 3proxy-0.9.3;sudo make -f Makefile.Linux;sudo make -f Makefile.Linux install;cd ~;mkdir 3pro;cd 3pro;touch 3proxy.cfg")

            print(ip)
    except Exception as e:
        print(e)


def start_of_proxy_config(ip):

    try:
            hostname = ip.split(':')[0]
            myuser   = 'root'
            mySSHK   = paramiko.RSAKey.from_private_key(StringIO(ip.split(':')[1]))

            sshcon   = paramiko.SSHClient()  # will create the object
            sshcon.set_missing_host_key_policy(paramiko.AutoAddPolicy()) # no known_hosts error

            sshcon.connect(hostname, username=myuser, pkey=mySSHK) # no passwd needed

            def run_command_on_ssh_server(command, ssh=sshcon):
                stdin, stdout, stderr = ssh.exec_command(command)
                exit_status = stdout.channel.recv_exit_status()
                print(exit_status)

            ftp = sshcon.open_sftp()
            file=ftp.file('3proxy.cfg', "a", -1)
            file.write("""daemon\nlogformat "L%C - %U [%d/%o/%Y:%H:%M:%S %z] ""%T"" %E %I %O %N/%R:%r"\nlog c:\3proxy\logs\3proxy.log D\nrotate 30\nauth none\nproxy""")
            file.flush()
            ftp.close()
            print(str(ip))
            run_command_on_ssh_server("cd ~;3proxy ~/3proxy.cfg")
    except Exception as e:
        print(e)


def create_servers(token, geo):
    print(token)
    manager = digitalocean.Manager(token=token)
    keys = manager.get_all_sshkeys()

    droplet = digitalocean.Droplet()



    for i in range(3):
        try:
            droplet = digitalocean.Droplet(token=manager.token,
                                       name= str(random.randint(111111, 999999)),
                                       region=geo, # Amster
                                       image='ubuntu-20-04-x64', # Ubuntu 20.04 x64
                                       size_slug='s-1vcpu-2gb',  # 1GB RAM, 1 vCPU
                                       ssh_keys=keys, #Automatic conversion
                                       backups=False)
            time.sleep(random.randint(1, 10))
            droplet.create()

        except Exception as e:
            print(e)

def delete_proxies(token):
    do = DoManager(None, token, api_version=2)
    manager = digitalocean.Manager(token=token)

    my_droplets = manager.get_all_droplets()

    for i in my_droplets:
        print(i.id)
        do.destroy_droplet(i.id)

    return print('all droplets were succesfully deleted have fun')


def multi_setup_servers(tokens):
    ips = []

    for i in tokens:
        for a in list_of_active_servers(i):
            ips.append(a)

    p = Pool(len(ips))
    p.map(setup_servers, ips)

def multi_proxy_start(tokens):
    ips = []

    for i in tokens:
        for a in list_of_active_servers(i):
            ips.append(a)

    p = Pool(len(ips))
    p.map(start_of_proxy_config, ips)
    return ips

def check_id_tokens_valid(token_list):
    valid_tokens = []
    unvalid_tokens = []
    for token in token_list:

        do = DoManager(None, token, api_version=2)
        manager = digitalocean.Manager(token=token)
        try:
            manager.get_all_droplets()
            valid_tokens.append(str(token))
        except Exception as e:
            unvalid_tokens.append(str(token))

    return [valid_tokens, unvalid_tokens]

def add_openssh_to_account(token):
    if check_if_token_in_bd(token.strip()) == 0:
        generated_key = RSA.generate(2048, os.urandom)

        open_ssh = str(generated_key.exportKey('OpenSSH').decode())
        private_key = generated_key.exportKey('PEM').decode()

        key = SSHKey(token=token,
                     name=str(random.randint(111111, 999999)),
                     public_key=open_ssh)

        key.create()

        add_token(token, open_ssh, private_key)

