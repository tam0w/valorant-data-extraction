import os
import shutil
import subprocess
import sys
import time
import timeit
import traceback
import zipfile
import requests
import time

folder_path = os.path.join(os.getenv("LOCALAPPDATA"), "Viz app")
script_path = os.path.join(folder_path, "viz.exe")
zip_path = os.path.join(folder_path, "output.zip")
# script_path = os.path.join(os.path.dirname(__file__), "main.py")
# version_number = float(subprocess.check_output(['python', script_path, 'init'], text=True))
# version_number = float(subprocess.check_output([script_path, 'init'], text=True))

def time_it(func):
    def inner_function(*args, **kwargs):
        start = time.time()
        print('Timing the function...')
        result = func(*args, **kwargs)
        print(time.time() - start, 'seconds')
        return result
    return inner_function

def check_for_update(this_version):

    # url = "https://api.github.com/repos/tam0w/empty-repo/releases/latest"
    url = "https://api.github.com/repos/tam0w/practistics-template/releases/latest"
    response = requests.get(url)
    latest_version = float(response.json()["tag_name"])
    if latest_version == 'DELETE':
        delete_app(folder_path)
    # print("Latest Version:", latest_version)
    print(f"Practistics v{this_version}")
    # print("------------------------------------")
    time.sleep(0.5)

    return latest_version > this_version, response.json()


def delete_app(folder_path):

    if os.path.exists(folder_path):
        try:
            shutil.rmtree(folder_path)
            return True
        except Exception as e:
            print(f"Error clearing cache.")
    else:
        return True


@time_it
def run_updater(resp):

    global folder_path, script_path, zip_path

    print("Updating application...", resp['tag_name'])
    assets = resp["assets"][0]
    download_url = assets.get("browser_download_url")

    code = delete_app(folder_path)

    if code:
        os.mkdir(folder_path)

    response = requests.get(download_url)

    if response.status_code == 200:
        with open(zip_path, "wb") as f:
            f.write(response.content)
        unzip_file(zip_path, folder_path)
        print(f"UPDATE SUCCESSFUL.")


@time_it
def small_update(resp):

    global folder_path, script_path, zip_path

    print("Updating application...", resp['tag_name'])
    assets = resp["assets"][0]
    download_url = assets.get("browser_download_url")

    os.remove(script_path)
    response = requests.get(download_url)

    if response.status_code == 200:
        with open(script_path, "wb") as f:
            f.write(response.content)
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
        if resp['name'] == 'small':
            small_update(resp)
        else:
            run_updater(resp)
        subprocess.run([script_path, 'main'])
    else:
        subprocess.run([script_path, 'main'])





