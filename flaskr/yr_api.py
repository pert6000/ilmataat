
import requests

def main():
    url = 'SOME URL'

    headers = {
        'User-Agent': 'My User Agent 1.0',
        'From': 'youremail@domain.example'  # This is another valid field
    }

    response = requests.get(url, headers=headers)

    print(response.status_code
          )

if __name__ == '__main__':
    main()