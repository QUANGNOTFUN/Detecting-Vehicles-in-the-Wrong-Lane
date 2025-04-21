import os
import requests

def download_font(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded {filename}")
    else:
        print(f"Failed to download {filename}")

# URLs cho font Roboto
fonts = {
    "Roboto-Regular.ttf": "https://raw.githubusercontent.com/googlefonts/roboto/main/src/hinted/Roboto-Regular.ttf",
    "Roboto-Medium.ttf": "https://raw.githubusercontent.com/googlefonts/roboto/main/src/hinted/Roboto-Medium.ttf",
    "Roboto-Bold.ttf": "https://raw.githubusercontent.com/googlefonts/roboto/main/src/hinted/Roboto-Bold.ttf"
}

# Tạo thư mục fonts nếu chưa tồn tại
os.makedirs("assets/fonts", exist_ok=True)

# Tải các font
for font_name, url in fonts.items():
    download_font(url, f"assets/fonts/{font_name}")

print("Font download completed!") 