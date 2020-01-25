import re
import os
from datetime import date
from f5.bigip import ManagementRoot
from keyvault import GetSecret
from upload_to_blob import UploadToBlob

class F5():
    """This class is used to interact with an F5 appliance"""

    def __init__(self, username, password):
        """Initializes the F5 class"""
        self.username = username
        self.password = password
        F5.connect_to_f5(self)

    def connect_to_f5(self):
        """This function creates connects to the F5 appliance using the F5 SDK"""

        # Connect to the BigIP
        self.mgmt = ManagementRoot("localhost", self.username, self.password, port=5556, verify=False)

        # Get current date and time
        current_date = str(date.today())

        # Obtain Hostname, use regex to ignore the DNS name
        settings = self.mgmt.tm.sys.global_settings.load()
        hostname = settings.hostname
        hostname_clean = re.compile('[a-zA-Z,\d\_\-]+')
        hostname_clean = hostname_clean.findall(hostname)
        self.hostname = hostname_clean[0] + "-" + current_date
        F5.create_and_download_file(self)

    def create_and_download_file(self):
        """This function creates a UCS archive on an F5 downloads it locally"""

        # Create a new UCS file with the current date and hostname as the filename
        self.mgmt.tm.sys.ucs.exec_cmd('save', name=f'{self.hostname}.ucs')
        print(f"UCS Archive {self.hostname}.ucs has been created.\n")

        # Get a list of all the UCS files on the F5s local storage
        ucs = self.mgmt.tm.sys.ucs.load()
        items = ucs.items

        print("Current UCS Archive files stored on the F5:\n--")
        for item in items:
            print(item["apiRawValues"]["filename"])

        # Download the file to local storage
        print(f"\nDownloading UCS Archive {self.hostname}.ucs...")
        self.mgmt.shared.file_transfer.ucs_downloads.download_file(f'{self.hostname}.ucs', f'{self.hostname}.ucs')
        print(f"UCS Archive {self.hostname}.ucs has been downloaded locally.\n")
        F5.upload_file(self)

    def upload_file(self):
        """This function calls the UploadToBlob class to upload the UCS file to an Azure storage blob"""

        self.container_name = os.getenv('AZURE_STORAGE_CONTAINER_NAME')

        UploadToBlob.upload_file(self)
        # Upload the file to an Azure Storage Blob using the UploadToBlob class.
        F5.clean_up(self)

    def clean_up(self):
        """This function performs clean up activities"""

        # Delete created UCS Archive from F5 appliance and from local storage
        self.mgmt.tm.util.bash.exec_cmd('run', utilCmdArgs=f'-c "rm /var/local/ucs/{self.hostname}.ucs"')
        os.remove(f"{self.hostname}.ucs")
        print(f"UCS Archive {self.hostname}.ucs has been deleted from the F5s appliance and from local storage.\n")


F5_USERNAME = GetSecret("tactical-f5-user").secret_value
F5_PASSWORD = GetSecret("tactical-f5-pw").secret_value
F5(F5_USERNAME, F5_PASSWORD)
