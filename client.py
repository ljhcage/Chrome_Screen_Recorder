import requests
url = "http://127.0.0.1:7700/recoder"
path = "load.jpg"
print(path)
files = {'file': open(path, 'rb')}
r = requests.post(url, files=files)
print (r.url)
print (r.text)