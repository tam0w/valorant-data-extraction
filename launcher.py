import os
import subprocess
import sys
import time
import traceback
import zipfile
import requests

script_path = os.path.join(os.path.dirname(__file__), "practistics.exe")


def check_for_update(this_version):
    # Query GitHub API to get the latest release version
    url = "https://api.github.com/repos/tam0w/ci_cd_implementation/releases/latest"

    # github_token = "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"
    # headers = {'Authorization': f'token {github_token}'}
    response = requests.get(url)
    latest_version = float(response.json()["tag_name"])
    print("Update Checker:")
    print("Latest Version:", latest_version)
    print("Current Version:", this_version)
    print("------------------------------------")
    time.sleep(0.5)

    return latest_version > this_version, response.json()


def run_updater(resp):
    # Your update logic here
    print("Running updater...")
    assets = resp["assets"][0]
    download_url = assets.get("browser_download_url")
    os.remove("ci_cd.exe")

    local_filename = os.path.join(os.getcwd(), "ci_cd.exe")

    response = requests.get(download_url)

    if response.status_code == 200:
        with open(local_filename, "wb") as f:
            f.write(response.content)
        print(f"Download successful.")
    subprocess.run([script_path, 'main'])


def download_app(resp):
    print("Downloading app...")
    assets = resp["assets"][0]
    download_url = assets.get("browser_download_url")

    local_filename = os.path.join(os.getcwd(), "ci_cd.exe")

    response = requests.get(download_url)

    if response.status_code == 200:
        with open(local_filename, "wb") as f:
            f.write(response.content)
        print(f"Download successful.")


if not os.path.exists(script_path):
    download_app(requests.get("https://api.github.com/repos/tam0w/ci_cd_implementation/releases/latest").json())

version_number = float(subprocess.check_output([script_path, 'init'], text=True))

update, resp = check_for_update(version_number)

if update:
    run_updater(resp)
else:
    subprocess.run([script_path, 'main'])
