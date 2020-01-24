from f5.bigip import ManagementRoot
from keyvault import GetSecret

class F5():
    """This class is used to interact with an F5 appliance"""

    def __init__(self, password):
        """This function retrieves a secret from an Azure Key Vault"""
        self.password = password
        # Connect to the BigIP
        bigip = ManagementRoot("localhost", "admin", self.password, port=5556, verify=False)

        # Get a list of all pools on the BigIP and print their name and their
        # members' name
        pools = bigip.tm.ltm.pools.get_collection()
        for pool in pools:
            for member in pool.members_s.get_collection():
                print(member.name)

f5_password = GetSecret("reformMgmtF5Internal-password").secret_value
F5(f5_password)