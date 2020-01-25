import os, uuid
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError

class UploadToBlob():
    """This class is used to interact with Azure Storage Accounts"""

    def __init__(self):
        """This function uploads files to an Azure Storage Container blob"""

        self.container_name = os.getenv('AZURE_STORAGE_CONTAINER_NAME')
        self.connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connect_str)
        self.container = self.blob_service_client.get_container_client(container=self.container_name)
        self.generator = self.container.list_blobs()

    def upload_file(self, upload_file):
        """This function uploads a file to an Azure storage blob"""
        self.upload_file = upload_file
        self.blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=self.upload_file)

        try:
            # Upload the created file
            print(f"Uploading {self.upload_file} to Azure Storage blob...")
            with open(f"{self.upload_file}", "rb") as data:
                self.blob_client.upload_blob(data)
            print(f"UCS archive {self.upload_file} has been uploaded to Azure storage container {self.container_name}.")

        except ResourceExistsError:
            print(f"The file already exists in storage container {self.container_name} so it will not be uploaded.")

    def delete_file(self, delete_file):
        """This function deletes a file stored in an Azure storage blob"""
        self.delete_file = delete_file
        self.blob_client_delete = self.blob_service_client.get_blob_client(container=self.container_name, blob=self.delete_file)

        try:
            # Delete yesterday's UCS file
            self.blob_client_delete.delete_blob()
            print(f"UCS archive {self.delete_file} has been deleted from Azure storage container {self.container_name}.")

        except ResourceNotFoundError:
            pass
