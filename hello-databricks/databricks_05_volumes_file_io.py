"""
Step 5: file I/O against a Unity Catalog Volume.

Volumes are Databricks' successor to DBFS for arbitrary (non-tabular)
files. From your own machine there's no local mount for `/Volumes/...` —
that only exists on the cluster's own filesystem — so client-side access
goes through the Files API (databricks-sdk) instead of plain open().

Requires the volume from ../terraform:
    export DATABRICKS_VOLUME_PATH=$(terraform -chdir=../terraform output -raw volume_path)

Run:
    python3 databricks_05_volumes_file_io.py
"""
import io
import os

from databricks.sdk import WorkspaceClient

w = WorkspaceClient(
    host=os.environ["DATABRICKS_HOST"],
    token=os.environ["DATABRICKS_TOKEN"],
)

file_path = f"{os.environ['DATABRICKS_VOLUME_PATH']}/hello.txt"
contents = b"hello from hello-databricks step 5\n"

print(f"--- Uploading to {file_path} ---")
w.files.upload(file_path, io.BytesIO(contents), overwrite=True)

print("--- Downloading it back ---")
downloaded = w.files.download(file_path).contents.read()
print(downloaded.decode())

assert downloaded == contents, "round trip mismatch"
print("Round trip OK")
