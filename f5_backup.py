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
        mgmt = ManagementRoot("localhost", self.username, self.password, port=5556, verify=False)

        # Get current date and time
        current_date = str(date.today())
        
        # Obtain Hostname, use regex to ignore the DNS name
        settings = mgmt.tm.sys.global_settings.load()
        hostname = settings.hostname
        hostname_clean = re.compile('[a-zA-Z,\d\_\-]+')
        hostname_clean = hostname_clean.findall(hostname)
        hostname_clean[0] = hostname_clean[0] + "-" + current_date
     
        # Create a new UCS file with the current date and hostname as the filename
        mgmt.tm.sys.ucs.exec_cmd('save', name=f'{hostname_clean[0]}.ucs')
        print(f"UCS Archive {hostname_clean[0]}.ucs has been created successfully.\n")

        # Upload the file to local storage
        mgmt.shared.file_transfer.ucs_downloads.download_file(f'{hostname_clean[0]}.ucs', f'{hostname_clean[0]}.ucs')
        print(f"UCS Archive {hostname_clean[0]}.ucs has been uploaded successfully.\n")

        # Delete created UCS Archive
        mgmt.tm.util.bash.exec_cmd('run', utilCmdArgs=f'-c "rm /var/local/ucs/{hostname_clean[0]}.ucs"')
        print(f"UCS Archive {hostname_clean[0]}.ucs has been deleted from the F5s local storage successfully.\n")

        # Get a list of all the UCS files on the F5s local storage
        ucs = mgmt.tm.sys.ucs.load()
        items = ucs.items
        
        print("Current UCS Archive files:\n--\n")
        for item in items:
            print(item["apiRawValues"]["filename"])


        
f5_username = GetSecret("tactical-f5-user").secret_value
f5_password = GetSecret("tactical-f5-pw").secret_value
F5(f5_username, f5_password)

