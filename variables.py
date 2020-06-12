import argparse
import os

class Parser():
    def __init__(self):
        pass
    
    def parse_var(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--KEY_VAULT_NAME")
        parser.add_argument("--AZURE_CLIENT_ID")
        parser.add_argument("--AZURE_CLIENT_SECRET")
        parser.add_argument("--AZURE_TENANT_ID")
        parser.add_argument("--AZURE_STORAGE_CONNECTION_STRING")
        parser.add_argument("--AZURE_STORAGE_CONTAINER_NAME")
        parser.add_argument("--F5_USERNAME")
        parser.add_argument("--F5_PASSWORD")
        parser.add_argument("--DEVICES")
        self.args = parser.parse_args()
        self.args.AZURE_CLIENT_ID = os.environ["AZURE_CLIENT_ID"]
        self.args.AZURE_CLIENT_SECRET = os.environ["AZURE_CLIENT_SECRET"]
        self.args.AZURE_TENANT_ID = os.environ["AZURE_TENANT_ID"]
        self.args.DEVICES = os.environ["devices"]
        self.args.F5_USERNAME = os.environ["F5_USERNAME"]
        self.args.F5_PASSWORD = os.environ["F5_PASSWORD"]
