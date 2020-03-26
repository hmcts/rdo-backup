import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError

class DownloadToBlob():
    """This class is used to interact with Azure Storage Accounts"""

    def __init__(self):
        """This function sets up the connection to the Azure storage container"""

        self.container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")
        self.connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connect_str)
        self.container = self.blob_service_client.get_container_client(container=self.container_name)
        self.generator = self.container.list_blobs()


    def download_file(self):
        """This function downloads a file from an Azure storage blob"""

        for blob in self.generator:
            if ".tfstate" in blob.name:
                self.blob_name = blob.name

        local_path = "."
        local_file_name = "tfstate.json"

        self.blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=self.blob_name)
        download_file_path = os.path.join(local_path, local_file_name)

        with open(download_file_path, "wb") as download_file:
            download_file.write(self.blob_client.download_blob().readall())

        
