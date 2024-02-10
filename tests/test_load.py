import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

def make_request(url):
    response = requests.get(url)
    return response.status_code

def main():
    url = "https://cool-chat.club/"  # Замініть на вашу URL-адресу
    number_of_requests = 500  # Кількість запитів

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request, url) for _ in range(number_of_requests)]
        for future in as_completed(futures):
            try:
                status_code = future.result()
                print(f"Response status code: {status_code}")
            except Exception as e:
                print(f"Request failed: {e}")

if __name__ == "__main__":
    main()
