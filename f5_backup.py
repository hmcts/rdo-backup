from f5.bigip import ManagementRoot
from keyvault import GetSecret
import re
from datetime import date

class F5():
    """This class is used to interact with an F5 appliance"""

    def __init__(self, username, password):
        """This function creates a UCS archive on an F5 and then uploads it to blob storage"""
        self.username = username
        self.password = password

        # Connect to the BigIP
        bigip = ManagementRoot("localhost", self.username, self.password, port=5556, verify=False)

        # Obtain Hostname, use regex to ignore the DNS name
        settings = bigip.tm.sys.global_settings.load()
        hostname = settings.hostname
        hostname_clean = re.compile('[a-zA-Z,\d\_\-]+')
        hostname_clean = hostname_clean.findall(hostname)

        # Get current date and time
        current_date = str(date.today())

        # Create a new UCS file with the current date and hostname as the filename
        bigip.tm.sys.ucs.exec_cmd('save', name=f'{hostname_clean[0]}-{current_date}.ucs')

        # Get a list of all the UCS files on the F5s local storage
        ucs = bigip.tm.sys.ucs.load()
        items = ucs.items
        for item in items:
            print(item["apiRawValues"]["filename"])

        
f5_username = GetSecret("tactical-f5-user").secret_value
f5_password = GetSecret("tactical-f5-pw").secret_value
F5(f5_username, f5_password)

#mgmt.shared.file_transfer.ucs_downloads.download_file('config.ucs', '/Users/citizenelah/Downloads/config.ucs')