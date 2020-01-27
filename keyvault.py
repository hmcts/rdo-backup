import os
import sys
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

        parser = argparse.ArgumentParser()
        parser.add_argument("--KEY_VAULT_NAME", "--AZURE_CLIENT_ID", "--AZURE_CLIENT_SECRET", "--AZURE_TENANT_ID")
        args = parser.parse_args()

        key_vault_name = args.KEY_VAULT_NAME
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
            
      