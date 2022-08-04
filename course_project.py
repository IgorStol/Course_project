from ya_disk import YandexDisk
from datetime import datetime
from time import sleep
import requests
import os


class Record:
    def __init__(self, likes: int, url: str):
        self.url = url
        self.vk_name = ""
        self.ya_name = ""
        self.likes = likes


class VK:
   def __init__(self, access_token, user_id, version='5.131'):
       self.token = access_token
       self.id = user_id
       self.version = version
       self.params = {'access_token': self.token, 'v': self.version}

   def users_info(self):
       url = 'https://api.vk.com/method/users.get'
       params = {'user_ids': self.id}
       response = requests.get(url, params={**self.params, **params})
       return response.json()

   def get_photos(self):
       url = 'https://api.vk.com/method/photos.get'
       params = {'owner_id': self.id, 'album_id': 'profile', 'extended': 1}
       response = requests.get(url, params={**self.params, **params})
       return response.json()


class TFile:
    def __init__(self, vk_name: str, likes: int):
        self.vk_name = vk_name
        self.likes = likes
        self.ya_name = ""


def gen_file_name(likes: int):
    d = datetime.now()
    s = str(d)
    s = s.replace('-', '_')
    s = s.replace(':', '_')
    s = s.replace(' ', '_')
    s = s.replace('.', '_')
    s = s+'_'+str(likes)
    s = s + ".jpg"
    sleep(0.05)
    return s


def add_mes(mes: str):
    print(mes)
    log_list.append(mes)


TOKEN_YA = ""
TOKEN_VK = ""
user_id = ""

log_list = []

"""Работаю с ВКонтакте"""
vk = VK(TOKEN_VK, user_id)
add_mes("Есть подключение к ВКонтакте")

records = []
data = vk.get_photos()
data = data['response']
data = data['items']
for photo in data:
    d = photo['likes']
    likes = d['count']
    arr = photo['sizes']
    for size in arr:
        if size['type'] == 'z':
            url = size['url']
            break
    rec = Record(likes, url)
    records.append(rec)
add_mes("Информация по фото получена")

"""Сохраняю файлы на жёсткий диск компьютера"""
ind = 0
for rec in records:
    file_name = str(ind) + '.jpg'
    rec.vk_name = file_name
    image_url = rec.url
    img_data = requests.get(image_url).content
    with open(file_name, 'wb') as handler:
        handler.write(img_data)
    add_mes("Файл "+file_name+" сохранен на жесткий диск")
    ind += 1

"""Формирую список лайков"""
like_list = []
for rec in records:
    like_list.append(rec.likes)
like_list.sort()
add_mes("Список лайков сформирован")

"""Формирую список повторов"""
rep_list = []
for i in range(len(like_list)-1):
    a = like_list[i]
    b = like_list[i+1]
    if a == b:
        rep_list.append(a)
rep_list = set(rep_list)
rep_list = list(rep_list)
add_mes("Список повторов сформирован")

"""Формирую имена файлов"""
for likes in rep_list:
    for rec in records:
        if likes == rec.likes:
            rec.ya_name = gen_file_name(likes)
            add_mes("Новое имя файла на базе лайков и даты сформировано: "+rec.ya_name)

for rec in records:
    if rec.ya_name == "":
        rec.ya_name = str(rec.likes)+".jpg"
        add_mes("Новое имя файла на базе лайков сформировано: "+rec.ya_name)

"""Переименовываю файлы на жёстком диске"""
for rec in records:
    old_name = rec.vk_name
    new_name = rec.ya_name
    os.rename(old_name, new_name)
    add_mes("Файл "+old_name+" переименован в "+new_name)

"""Загружаю файлы на Я.Диск"""
ya = YandexDisk(token=TOKEN_YA)
add_mes("Есть подключение к Яндекс.Диску")
for rec in records:
    path_to_file = rec.ya_name
    base_name = os.path.basename(path_to_file)
    disk_file_path = "VK/" + base_name
    ya.upload_file_to_disk(disk_file_path=disk_file_path, filename=path_to_file)
    add_mes("Файл "+base_name+" загружен на Яндекс.Диск")

"""Удаляю файлы с жесткого диска"""
for rec in records:
    os.remove(rec.ya_name)
    add_mes("Файл "+rec.ya_name+" удален с жесткого диска")
add_mes("Успех!")

"""Формирую log-файл на диске"""
f = open("log.txt", "w")
for mes in log_list:
    f.write(mes+"\n")
f.close()
