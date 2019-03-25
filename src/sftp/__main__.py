import os
import pysftp

path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)

hostname = "ftp.objectstore.eu"

tenant_id = os.getenv("GOB_OBJECTSTORE_TENANT_ID")
user = os.getenv("GOB_OBJECTSTORE_USER")
container_base = os.getenv("CONTAINER_BASE")

username = f"{tenant_id}:{user}"
password = os.getenv("GOB_OBJECTSTORE_PASSWORD")

cnopts = pysftp.CnOpts()
cnopts.hostkeys.load(f"{dir_path}/known_hosts")

print(f"Connect to {hostname} using {username}/{password}")
with pysftp.Connection(hostname, username=username, password=password, cnopts=cnopts) as sftp:
    with sftp.cd(container_base):
        sftp.put(__file__)
        dirs = sftp.listdir()
        print("Dirs", dirs)
