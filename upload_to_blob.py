import os, uuid
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import ResourceExistsError

class UploadToBlob():
    """This class is used to interact with Azure Storage Accounts"""

    def __init__(self):
        """This function uploads files to an Azure Storage Container blob"""
        
    def upload_file(self):
        """This function uploads the UCS file to an Azure storage blob"""

        connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        container = blob_service_client.get_container_client(container=self.container_name)
        blob_client = blob_service_client.get_blob_client(container=self.container_name, blob=f"{self.hostname}.ucs")
        generator = container.list_blobs()

        try:
            # Upload the created file
            print(f"Uploading {self.hostname} to Azure Storage blob...\n")
            with open(f"{self.hostname}.ucs", "rb") as data:
                blob_client.upload_blob(data)
            print(f"UCS Archive {self.hostname}.ucs has been uploaded to Azure storage container {self.container_name}.")

        except ResourceExistsError:
            print(f"That file already exists in {self.container_name} so it will not be uploaded to the blob storage.\nPerforming clean up activities...\n ")