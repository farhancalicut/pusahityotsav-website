# In storage_backends.py
from storages.backends.azure_storage import AzureStorage

class AzureMediaStorage(AzureStorage):
    account_name = 'your_azure_storage_account_name' # Will be set in environment variables
    account_key = 'your_azure_storage_account_key'   # Will be set in environment variables
    azure_container = 'media'
    expiration_secs = None