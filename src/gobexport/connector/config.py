import os

OBJECTSTORE_CONFIG = {
    "VERSION": '2.0',
    "AUTHURL": 'https://identity.stack.cloudvps.com/v2.0',
    "TENANT_NAME": os.getenv("GOB_OBJECTSTORE_TENANT_NAME"),
    "TENANT_ID": os.getenv("GOB_OBJECTSTORE_TENANT_ID"),
    "USER": os.getenv("GOB_OBJECTSTORE_USER"),
    "PASSWORD": os.getenv("GOB_OBJECTSTORE_PASSWORD"),
    "REGION_NAME": 'NL'
}
