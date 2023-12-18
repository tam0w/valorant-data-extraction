import os
import subprocess
import sys
import time
import traceback
import zipfile
import requests

folder_path = os.path.join(os.getenv("LOCALAPPDATA"), "Viz app")
script_path = os.path.join(folder_path, "viz.exe")
zip_path = os.path.join(folder_path, "output.zip")
# script_path = os.path.join(os.path.dirname(__file__), "main.py")
# version_number = float(subprocess.check_output(['python', script_path, 'init'], text=True))
# version_number = float(subprocess.check_output([script_path, 'init'], text=True))


def check_for_update(this_version):

    url = "https://api.github.com/repos/tam0w/empty-repo/releases/latest"
    response = requests.get(url)
    latest_version = float(response.json()["tag_name"])
    # print("Latest Version:", latest_version)
    print(f"Practistics v{this_version}")
    # print("------------------------------------")
    time.sleep(0.5)

    return latest_version > this_version, response.json()

def run_updater(resp):

    global folder_path, script_path, zip_path

    print("Updating application...")
    assets = resp["assets"][0]
    download_url = assets.get("browser_download_url")

    if os.path.exists(folder_path):
        try:
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    os.rmdir(item_path)
        except Exception as e:
            print(f"Error updating.")

    else:
        os.mkdir(folder_path)

    response = requests.get(download_url)

    if response.status_code == 200:
        with open(zip_path, "wb") as f:
            f.write(response.content)
        unzip_file(zip_path, folder_path)
        print(f"UPDATE SUCCESSFUL.")

def download_app(resp):
    print("Downloading app...")
    assets = resp["assets"][0]
    download_url = assets.get("browser_download_url")

    global folder_path, zip_path

    response = requests.get(download_url)

    if response.status_code == 200:
        with open(zip_path, "wb") as f:
            f.write(response.content)
        unzip_file(zip_path, folder_path)
        print(f"Download successful.".upper())


def unzip_file(zip_path, extract_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    os.remove(zip_path)
while True:

    if not os.path.exists(script_path):
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
        download_app(requests.get("https://api.github.com/repos/tam0w/empty-repo/releases/latest").json())

    version_number = float(subprocess.check_output([script_path, 'init'], text=True))
    update, resp = check_for_update(version_number)

    if update:
        run_updater(resp)
        subprocess.run([script_path, 'main'])
    else:
        subprocess.run([script_path, 'main'])





