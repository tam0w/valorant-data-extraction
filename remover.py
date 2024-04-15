import os, zipfile, requests

folder_path = os.path.join(os.getenv("LOCALAPPDATA"), "awesomenewfolderthatiwannamke")
script_path = os.path.join(folder_path, "text.txt")
zip_path = os.path.join(folder_path, "output.zip")

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

download_app(requests.get("https://api.github.com/repos/tam0w/empty-repo/releases/latest").json())
