from f5.bigip import ManagementRoot
from keyvault import GetSecret

class F5():
    """This class is used to interact with an F5 appliance"""

    def __init__(self, username, password):
        """This function creates a UCS archive on an F5 and then uploads it to blob storage"""
        self.username = username
        self.password = password

        # Connect to the BigIP
        bigip = ManagementRoot("localhost", self.username, self.password, port=5556, verify=False)

        # Get a list of all the UCS files on the F5s local storage
        ucs = bigip.tm.sys.ucs.load()
        items = ucs.items
        for item in items:
            print(item["apiRawValues"]["filename"])

f5_username = GetSecret("tactical-f5-user").secret_value
f5_password = GetSecret("tactical-f5-pw").secret_value
F5(f5_username, f5_password)

#mgmt.shared.file_transfer.ucs_downloads.download_file('config.ucs', '/Users/citizenelah/Downloads/config.ucs')