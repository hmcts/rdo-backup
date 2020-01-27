import os
import argparse 
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ResourceNotFoundError

class GetSecret():
    """This class is used to interact with Azure Key Vaults"""

    def __init__(self, secret_name, secret_value=''):
        """This function retrieves a secret from an Azure Key Vault"""
        self.secret_name = secret_name
        self.secret_value = secret_value

        key_vault_name = os.environ["KEY_VAULT_NAME"]
        kv_uri = f"https://{key_vault_name}.vault.azure.net"
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=kv_uri, credential=credential)

        try:
            retrieved_secret = client.get_secret(self.secret_name)
        except ResourceNotFoundError:
            print("Key not found, please verify that the key names are correct")
            exit(0)
        else:
            self.secret_value = retrieved_secret.value
    
    def parse_argument():
       parse = argparse.ArgumentParser(description="Test")
       parse.add_parameter("KEY_VAULT_NAME")
