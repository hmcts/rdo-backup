import os
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ResourceNotFoundError

class GetSecret():
    """This class is used to interact with Azure Key Vaults"""

    def __init__(self, secret_name):
        """This function retrieves a secret from an Azure Key Vault"""
        self.secret_name = secret_name

        key_vault_name = os.environ["KEY_VAULT_NAME"]
        kv_uri = f"https://{key_vault_name}.vault.azure.net"
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=kv_uri, credential=credential)

        # client.set_secret("secretName", "secretValue")
        try:
            retrieved_secret = client.get_secret("reformMgmtF5Internal-password")
        except ResourceNotFoundError:
            print("Key not found, please double check")
        else:
            print(retrieved_secret.name)
            print(retrieved_secret.value)