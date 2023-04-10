import requests

url = "https://poweroutage.us/"
response = requests.get(url)

if response.status_code == 200:
    # Do something with the HTML code
    print("YOU ARE IN")
else:
    # Handle the error
    print("ERROR")
