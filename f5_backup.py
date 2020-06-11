import re
import os
import sys
from datetime import date, timedelta
from f5.bigip import ManagementRoot
from icontrol.exceptions import iControlUnexpectedHTTPError
from requests import ConnectionError
from keyvault import GetSecret
from variables import Parser
from upload_to_blob import UploadToBlob
import urllib3
import threading
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

F5_USERNAME = self.args.F5_USERNAME
F5_PASSWORD = self.args.F5_PASSWORD
devices = self.args.devices
devices = devices.split(",")

class F5():
    """This class is used to interact with an F5 appliance"""

    def __init__(self, username, password, hostname=""):
        """Initializes the F5 class"""
        self.username = username
        self.password = password
        self.hostname = hostname

        F5.connect_to_f5(self)
        F5.create_and_download_file(self) 
        F5.upload_file(self)
        F5.clean_up(self)
        
    def connect_to_f5(self):
        """This function creates connects to the F5 appliance using the F5 SDK"""
        
        # Retrieve device list from a key vault secret and put them into a list
    
        try:
            # Connect to the BigIP
            self.mgmt = ManagementRoot(self.hostname, self.username, self.password, port=8443, verify=False)

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
            print("\n-----------------------------------------------------")
            print(f"Successfully logged into {self.hostname_clean[0]}.")
            print("-----------------------------------------------------\n")           
        
    def create_and_download_file(self):
        """This function creates a UCS archive on an F5 and downloads it locally"""
        try:
        # Create a new UCS file with the current date and hostname as the filename
            self.mgmt.tm.sys.ucs.exec_cmd('save', name=f'{self.hostname}.ucs')
        # Dirty hack - Sometimes the UCS file is too big resulting in a Rest timeout error. So we are
        # continuing after the event of a timeout error
        except iControlUnexpectedHTTPError:
            pass

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

    def upload_file(self):
        """This function calls the UploadToBlob class to upload the UCS file to an Azure storage blob"""

        # Upload the file to an Azure Storage Blob using the UploadToBlob class.
        UploadToBlob.upload_file(UploadToBlob(), f"{self.hostname}.ucs")

    def clean_up(self):
        """This function performs clean up activities"""

        # Delete created UCS archive from the F5 appliance, from local storage and from the Azure storage blob.
        print(f"\nPerforming clean up activities...")
        ucs = self.mgmt.tm.sys.ucs.load()
        items = ucs.items

        for item in items:
            if item["apiRawValues"]["filename"] != f"/var/local/ucs/{self.hostname}.ucs":
                self.mgmt.tm.util.bash.exec_cmd('run', utilCmdArgs=f'-c "rm {item["apiRawValues"]["filename"]}"')
            
                ucs_filename = re.compile('(?<=\/var\/local\/ucs\/).*')
                ucs_filename = ucs_filename.findall(item["apiRawValues"]["filename"])

                UploadToBlob.delete_file(UploadToBlob(), ucs_filename[0])
                print(f"UCS archive {item['apiRawValues']['filename']} has been deleted from {self.hostname_clean[0]}")
                
        print(f"UCS archive {self.hostname}.ucs has been deleted from local storage.\n")    
        os.remove(f"{self.hostname}.ucs")
        sys.exit()

if __name__ == "__main__":

    for device in devices:
        my_thread = threading.Thread(target=F5, args=(F5_USERNAME, F5_PASSWORD, device))
        my_thread.start()

    main_thread = threading.currentThread()
    for some_thread in threading.enumerate():
        if some_thread != main_thread:
            print(some_thread)
            some_thread.join()