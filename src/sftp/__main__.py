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

print(f"Connecting to {hostname} using {username}/{password}")
with pysftp.Connection(hostname, username=username, password=password, cnopts=cnopts) as sftp:
    print(f"Connected to {sftp}")
    with sftp.cd(container_base):
        print(f"Changed to {container_base}")
        dirs = sftp.listdir()
        print("Dirs", dirs)
        print(f"About to write {__file__}")
        result = sftp.put(__file__)
        print(f"Result: {result}")
        dirs = sftp.listdir()
        print("Dirs", dirs)
