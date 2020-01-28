import re
import os
from datetime import date, timedelta
from f5.bigip import ManagementRoot
from icontrol.exceptions import iControlUnexpectedHTTPError
from requests import ConnectionError
from keyvault import GetSecret
from upload_to_blob import UploadToBlob

class F5():
    """This class is used to interact with an F5 appliance"""

    def __init__(self, username, password, hostname=""):
        """Initializes the F5 class"""
        self.username = username
        self.password = password

        F5.connect_to_f5(self)

    def connect_to_f5(self):
        """This function creates connects to the F5 appliance using the F5 SDK"""
        devices = ["172.31.254.254", "172.16.15.254", "10.47.15.250", "10.29.0.254", "10.31.15.250", "10.31.15.252", "10.45.0.254", "10.47.15.252"]

        for device in devices:
            try:
                # Connect to the BigIP
                self.mgmt = ManagementRoot(device, self.username, self.password, port=8443, verify=False)

            except iControlUnexpectedHTTPError:
                print(f"Failed to login to the F5 appliance, please verify your credentials.")

            except ConnectionError:
                print(f"Failed to communicate with the F5 appliance, please verify connectivity.")

            else:
                # Get current date and time
                current_date = str(date.today())
                yesterdays_date = str(date.today() - timedelta(1))

                # Obtain Hostname, use regex to ignore the DNS name
                settings = self.mgmt.tm.sys.global_settings.load()
                hostname = settings.hostname
                hostname_clean = re.compile('[a-zA-Z,\d\_\-]+')
                self.hostname_clean = hostname_clean.findall(hostname)
                self.hostname = self.hostname_clean[0] + "-" + current_date
                self.yesterdays_file = self.hostname_clean[0] + "-" + yesterdays_date
                print("\n-----------------------------------------------------")
                print(f"Successfully logged into {self.hostname_clean[0]}.")
                print("-----------------------------------------------------\n")
                F5.create_and_download_file(self)            
        
    def create_and_download_file(self):
        """This function creates a UCS archive on an F5 and downloads it locally"""

        # Create a new UCS file with the current date and hostname as the filename
        self.mgmt.tm.sys.ucs.exec_cmd('save', name=f'{self.hostname}.ucs')
        print(f"Creating a new UCS archive on {self.hostname_clean[0]}...")
        print(f"UCS archive {self.hostname}.ucs has been created.\n")

        # Display a list of all the UCS files on the F5s local storage
        ucs = self.mgmt.tm.sys.ucs.load()
        items = ucs.items

        print(f"Current UCS archive files stored on {self.hostname_clean[0]}:\n--")
        for item in items:
            print(item["apiRawValues"]["filename"])

        # Download the file to local storage
        print(f"\nDownloading UCS archive {self.hostname}.ucs...")
        self.mgmt.shared.file_transfer.ucs_downloads.download_file(f'{self.hostname}.ucs', f'{self.hostname}.ucs')
        print(f"UCS archive {self.hostname}.ucs has been downloaded locally.\n")
        F5.upload_file(self)

    def upload_file(self):
        """This function calls the UploadToBlob class to upload the UCS file to an Azure storage blob"""

        # Upload the file to an Azure Storage Blob using the UploadToBlob class.
        UploadToBlob.upload_file(UploadToBlob(), f"{self.hostname}.ucs")
        F5.clean_up(self)

    def clean_up(self):
        """This function performs clean up activities"""

        # Delete created UCS archive from the F5 appliance, from local storage and from the Azure storage blob.
        self.mgmt.tm.util.bash.exec_cmd('run', utilCmdArgs=f'-c "rm /var/local/ucs/{self.yesterdays_file}.ucs"')
        os.remove(f"{self.hostname}.ucs")
    
        print(f"\nPerforming clean up activities...")
        UploadToBlob.delete_file(UploadToBlob(), f"{self.yesterdays_file}.ucs")
        print(f"UCS archive {self.yesterdays_file}.ucs has been deleted from {self.hostname_clean[0]}")
        print(f"UCS archive {self.hostname}.ucs has been deleted from local storage.\n")

F5_USERNAME = GetSecret("tactical-f5-user").secret_value
F5_PASSWORD = GetSecret("tactical-f5-pw").secret_value
F5(F5_USERNAME, F5_PASSWORD)
