import os
import subprocess
import sys
import time
import traceback
import zipfile
import requests

folder_path = os.path.join(os.getenv("LOCALAPPDATA"), "ApplicationVizIns")
script_path = os.path.join(folder_path, "practistics.exe")
zip_path = os.path.join(folder_path, "output.zip")
# script_path = os.path.join(os.path.dirname(__file__), "main.py")
# version_number = float(subprocess.check_output(['python', script_path, 'init'], text=True))
version_number = float(subprocess.check_output([script_path, 'init'], text=True))

def check_for_update(this_version):

    url = "https://api.github.com/repos/tam0w/demo_analysis_TL/releases/latest"
    response = requests.get(url)
    latest_version = float(response.json()["tag_name"])
    print("Update Checker:")
    print("Latest Version:", latest_version)
    print("Current Version:", this_version)
    print("------------------------------------")
    time.sleep(0.5)

    return latest_version > this_version, response.json()

def run_updater(resp):

    global folder_path, script_path, zip_path

    print("Running updater...")
    assets = resp["assets"][0]
    download_url = assets.get("browser_download_url")
    os.remove(folder_path)

    response = requests.get(download_url)

    if response.status_code == 200:
        with open(folder_path, "wb") as f:
            f.write(response.content)
        print(f"Download successful.")
    subprocess.run([script_path, 'main'])


def download_app(resp):
    print("Downloading app...")
    assets = resp["assets"][0]
    download_url = assets.get("browser_download_url")

    global folder_path, zip_path

    response = requests.get(download_url)

    if response.status_code == 200:
        with open(folder_path, "wb") as f:
            f.write(response.content)
            unzip_file(zip_path, folder_path)
        print(f"Download successful.")


def unzip_file(zip_path, extract_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    os.remove(zip_path)


def auth():
    key = input('Insert your authentication key:')
    header = {'Authorization': f'Bearer {key}'}
    test = requests.post('https://practistics.live/app/api/verify', headers=header)

    if test.status_code == 200:
        return key

    else:
        print('Token expired / invalid.')
        return 0

jwt = 0

while True:
    subprocess.run([script_path, 'init'])
    if jwt == 0:
        jwt = auth()
        continue

    ans = input('Please type \'start\' when you would like to begin or \'exit\' if you are finished.\n')
    if ans == 'start':
        try:
            # if not os.path.exists(script_path):
            #     download_app(requests.get("https://api.github.com/repos/tam0w/demo_analysis_TL/releases/latest").json())
            #
            # update, resp = check_for_update(version_number)
            #
            # if update:
            #     run_updater(resp)
            # else:
            #     subprocess.run([script_path, 'main'])
            subprocess.run([script_path, 'main'])
        except Exception:
            traceback.print_exc()
            continue

    if ans == 'exit':
        break





if not os.path.exists(script_path):
    download_app(requests.get("https://api.github.com/repos/tam0w/demo_analysis_TL/releases/latest").json())

version_number = float(subprocess.check_output([script_path, 'init'], text=True))

update, resp = check_for_update(version_number)

if update:
    run_updater(resp)
# else:
    subprocess.run([script_path, 'main'])
