from netmiko import ConnectHandler
from functions import *
from log import *
from strings import *
from auth import *

import os
import traceback
import re

shHostname = "show run | i hostname"
showIntVlan = "show run | sec interface Vlan"

delDHCPList = [
    'no ip helper-address 10.0.0.0'
]

def delDHCPSevers(validIPs, username, netDevice):
    # This function is to add Auto Recovery
    
    for validDeviceIP in validIPs:
        try:
            validDeviceIP = validDeviceIP.strip()
            currentNetDevice = {
                'device_type': 'cisco_xe',
                'ip': validDeviceIP,
                'username': username,
                'password': netDevice['password'],
                'secret': netDevice['secret'],
                'global_delay_factor': 2.0,
                'timeout': 120,
                'session_log': 'netmikoLog.txt',
                'verbose': True,
                'session_log_file_mode': 'append'
            }

            print(f"INFO: Connecting to device {validDeviceIP}...")
            authLog.info(f"User {username} is now running commands at: {validDeviceIP}")
            with ConnectHandler(**currentNetDevice) as sshAccess:
                sshAccess.enable()
                showIntVlanOut = sshAccess.send_command(showIntVlan)
                authLog.info(f"User {username} connected to {validDeviceIP} ran the command '{showIntVlan}'")
                print(showIntVlanOut)
                os.system("PAUSE")
                showIntVlanOut = showIntVlanOut.replace('ip helper-address 192.168.0.1','no ip helper-address 192.168.0.1')
                authLog.info(f"Automation removed the ip helpers in device{validDeviceIP}: ")
                print(showIntVlanOut)
                os.system("PAUSE")

                shHostnameOut = sshAccess.send_command(shHostname)
                authLog.info(f"User {username} successfully found the hostname {shHostnameOut}")
                shHostnameOut = shHostnameOut.replace('hostname ', '')
                shHostnameOut = shHostnameOut.strip()
                shHostnameOut = shHostnameOut + "#"

                print(f"INFO: Configuring the following commands in {validDeviceIP}: {delDHCPList[0]}")
                authLog.info(f"Configuring the following commands in {validDeviceIP}: {delDHCPList[0]}")
                showIntVlanOut = showIntVlanOut.split('\n')
                showDelDHCP = sshAccess.send_config_set(showIntVlanOut)
                print(showDelDHCP)
                os.system("PAUSE")
                print(f"INFO: Successfully removed unnecessary DHCP servers for device: {validDeviceIP}")
                authLog.info(f"Successfully removed unnecessary DHCP servers for device: {validDeviceIP}")

                with open(f"{validDeviceIP}_Outputs.txt", "a") as file:
                    file.write(f"User {username} connected to device IP {validDeviceIP}\n\n")
                    print(f"INFO: Validating the configuration done...\n{shHostnameOut}{showIntVlan}")
                    showIntVlanOut = sshAccess.send_command(showIntVlan)
                    authLog.info(f"Automation successfully ran the command: {showIntVlan}")
                    file.write(f"{shHostnameOut}{showIntVlan}:\n{showIntVlanOut}")

        except Exception as error:
            print(f"An error occurred: {error}\n", traceback.format_exc())
            authLog.error(f"User {username} connected to {validDeviceIP} got an error: {error}")
            authLog.debug(traceback.format_exc(),"\n")
            with open(f"failedDevices.csv","a") as failedDevices:
                failedDevices.write(f"{validDeviceIP}\n")
        
        finally:
            with open(f"generalOutputs.txt", "a") as file:
                    file.write(f"INFO: Taking a \"{showIntVlan}\" for device: {validDeviceIP}\n")
                    file.write(f"{shHostnameOut}{showIntVlan}:\n{showIntVlanOut}\n")
            print("\nOutputs and files successfully created.")
            print("For any erros or logs please check authLog.txt\n")