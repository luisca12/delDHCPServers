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
    '10.155.23.120',
    '30.230.62.110',
    '30.232.62.126',
    '30.132.252.110'
]

delDHCPCommands = {
    f'ip helper-address {delDHCPList[0]}':f'no ip helper-address {delDHCPList[0]}',
    f'ip helper-address {delDHCPList[1]}':f'no ip helper-address {delDHCPList[1]}',
    f'ip helper-address {delDHCPList[2]}':f'no ip helper-address {delDHCPList[2]}',
    f'ip helper-address {delDHCPList[3]}':f'no ip helper-address {delDHCPList[3]}'
}

commandList = '\n'.join(list(delDHCPCommands.values()))

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
                oldConfig = showIntVlanOut
                authLog.info(f"User {username} connected to {validDeviceIP} ran the command '{showIntVlan}'")
                shHostnameOut = sshAccess.send_command(shHostname)
                authLog.info(f"User {username} successfully found the hostname {shHostnameOut}")
                shHostnameOut = shHostnameOut.replace('hostname ', '')
                shHostnameOut = shHostnameOut.strip()
                shHostnameOut = shHostnameOut + "#"

                print(f"INFO: Configuring the following commands in {validDeviceIP}\n{commandList}")
                showIntVlanOut = showIntVlanOut.replace(list(delDHCPCommands.keys())[0], list(delDHCPCommands.values())[0])
                showIntVlanOut = showIntVlanOut.replace(list(delDHCPCommands.keys())[1], list(delDHCPCommands.values())[1])
                showIntVlanOut = showIntVlanOut.replace(list(delDHCPCommands.keys())[2], list(delDHCPCommands.values())[2])
                showIntVlanOut = showIntVlanOut.replace(list(delDHCPCommands.keys())[3], list(delDHCPCommands.values())[3])
                authLog.info(f"Automation removed the ip helpers {delDHCPList[0]}, {delDHCPList[1]}, {delDHCPList[2]}, and {delDHCPList[3]} in device {validDeviceIP}: ")

                showIntVlanOut = showIntVlanOut.split('\n')
                showDelDHCP = sshAccess.send_config_set(showIntVlanOut)
                print(f"INFO: Successfully removed unnecessary DHCP servers for device: {validDeviceIP}")
                authLog.info(f"Successfully removed unnecessary DHCP servers for device: {validDeviceIP}")
                authLog.info(f"The following configuration was sent to the device: {validDeviceIP}\n{showDelDHCP}")

                with open(f"{validDeviceIP}_Outputs.txt", "a") as file:
                    file.write(f"User {username} connected to device IP {validDeviceIP}\n\n")
                    file.write(f"INFO: Old/Current configuration:\n{shHostnameOut}{showIntVlan}\n{oldConfig}\n")
                    print(f"INFO: Validating the new configuration done...\n{shHostnameOut}{showIntVlan}")
                    showIntVlanOut1 = sshAccess.send_command(showIntVlan)
                    print(showIntVlanOut1)
                    authLog.info(f"Automation successfully ran the command: \"{showIntVlan}\" to validate the new configuration:\n\
                    {shHostnameOut}{showIntVlan}:\n{showIntVlanOut1}")
                    file.write("\nINFO: Validating the new configuration:\n")
                    file.write(f"{shHostnameOut}{showIntVlan}:\n{showIntVlanOut1}")

        except Exception as error:
            print(f"An error occurred: {error}\n", traceback.format_exc())
            authLog.error(f"User {username} connected to {validDeviceIP} got an error: {error}")
            authLog.debug(traceback.format_exc(),"\n")
            with open(f"failedDevices.csv","a") as failedDevices:
                failedDevices.write(f"{validDeviceIP}\n")
        
        finally:
            with open(f"generalOutputs.txt", "a") as file:
                    file.write(f"INFO: Taking a \"{showIntVlan}\" for device: {validDeviceIP}\n")
                    file.write(f"{shHostnameOut}{showIntVlan}:\n{showIntVlanOut1}\n")
            print("\nOutputs and files successfully created.")
            print("For any erros or logs please check authLog.txt\n")