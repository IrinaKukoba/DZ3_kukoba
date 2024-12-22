import requests
import json
from tqdm import tqdm


# Функция для создания папки на диске
def create_folder_on_yandex(token, folder_name):
    url = "https://cloud-api.yandex.net/v1/disk/resources"
    headers = {
        "Authorization": f"OAuth {token}"
    }
    params = {
        "path": folder_name,
        "overwrite": "true"
    }
    response = requests.put(url, headers=headers, params=params)
    if response.status_code == 201:
        print(f"Папка '{folder_name}' успешно создана на Яндекс.Диске.")
    else:
        print(f"Ошибка при создании папки: {response.text}")


# Функция для загрузки фотографии на диск
def upload_photo_to_yandex(token, file_url, folder_name, file_name):
    url = f"https://cloud-api.yandex.net/v1/disk/resources/upload"
    headers = {
        "Authorization": f"OAuth {token}"
    }
    params = {
        "path": f"{folder_name}/{file_name}",
        "url": file_url
    }
    response = requests.post(url, headers=headers, params=params)
    if response.status_code == 202:
        print(f"Фотография '{file_name}' успешно загружена на диск.")
    else:
        print(f"Ошибка при загрузке фотографии: {response.text}")


# Функция для получения всех фотографий с ВК
def get_photos(vk_user_id, vk_token, yandex_token, count=5):
    vk_url = f'https://api.vk.com/method/photos.get'
    params = {
        'owner_id': int(vk_user_id),
        'album_id': 'profile',
        'access_token': vk_token,
        'v': '5.131'
    }

    response = requests.get(vk_url, params=params)
    print("Ответ от VK API:", response.json())  

    if response.status_code != 200:
        print(f"Ошибка при запросе к VK API: {response.status_code} - {response.text}")
        return

    data = response.json()

    if 'error' in data:
        print(f"Ошибка в ответе API VK: Код ошибки {data['error']['error_code']} - {data['error']['error_msg']}")
        return

    photos = data['response']['items']


    if not photos:
        print("Нет фотографий для загрузки.")
        return

    folder_name = 'vk_photos'
    create_folder_on_yandex(yandex_token, folder_name)

    photo_info = []

    for index, photo in tqdm(enumerate(photos), desc="Загрузка фотографий"):
  
        max_size = max(photo['sizes'], key=lambda x: x['width'] * x['height'])

        file_name = f"{photo['likes']['count']}.jpg" if 'likes' in photo else f"photo_{index}.jpg"

        file_url = max_size['url']  

        upload_photo_to_yandex(yandex_token, file_url, folder_name, file_name)

        photo_info.append({
            "file_name": file_name,
            "size": max_size['type']
        })

    try:
        with open('photo_info.json', 'w') as f:
            json.dump(photo_info, f, indent=4)
        print(f"Информация о фотографиях сохранена в 'photo_info.json'.")
    except Exception as e:
        print(f"Ошибка при записи в файл photo_info.json: {e}")

if __name__ == "__main__":
    vk_user_id = input("Введите id пользователя: ")  
    vk_token = "763a0a09763a0a09763a0a0917751cd2557763a763a0a0911520633485286a1707ca55b"  
    yandex_token = input("Введите токен яндекс диска: ") 
    get_photos(vk_user_id, vk_token, yandex_token)
