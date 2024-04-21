import os, zipfile, requests
import shutil
import time

folder_path = os.path.join(os.getenv("LOCALAPPDATA"), "Viz app")
script_path = os.path.join(folder_path, "viz.exe")
zip_path = os.path.join(folder_path, "output.zip")

def check_for_update(this_version):

    url = "https://api.github.com/repos/tam0w/empty-repo/releases/latest"
    response = requests.get(url)
    latest_version = float(response.json()["tag_name"])
    if latest_version == 'DELETE':
        delete_app(folder_path)
    # print("Latest Version:", latest_version)
    print(f"Practistics v{this_version}")
    # print("------------------------------------")
    time.sleep(0.5)

    return latest_version > this_version, response.json()

def download_app(resp):
    print("Downloading app...")
    assets = resp["assets"][0]
    download_url = assets.get("browser_download_url")

    global folder_path, zip_path

    response = requests.get(download_url)

    if response.status_code == 200:
        with open(folder_path, "wb") as f:
            f.write(response.content)
            print("Download huva abhi unzip")
        unzip_file(zip_path, folder_path)
        print(f"Download successful.")

def unzip_file(zip_path, extract_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    os.remove(zip_path)

def run_updater(resp):

    global folder_path, script_path, zip_path

    print("Updating application...")
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

def delete_app(folder_path):

    if os.path.exists(folder_path):
        try:
            shutil.rmtree(folder_path)
            return False
        except Exception as e:
            print(e)
    else:
        return True

# download_app(requests.get("https://api.github.com/repos/tam0w/empty-repo/releases/latest").json())
print(check_for_update(1.5))