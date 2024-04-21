import zipfile
import os

appdata_path = os.path.join(os.getenv("LOCALAPPDATA"), "Viz app")


def unzip_file(zip_path, extract_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

# Example: Unzip 'output.zip' to a folder named 'extracted_folder'
unzip_file('output.zip', appdata_path)
