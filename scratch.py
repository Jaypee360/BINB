import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
response = requests.get('https://brandondowntown.biz/event/', headers=headers)
print(f"Status Code: {response.status_code}")

with open('scratch_requests.html', 'w', encoding='utf-8') as f:
    f.write(response.text)
