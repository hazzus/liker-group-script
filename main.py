import vk
import time
from urllib.parse import urlparse

from vk.exceptions import  VkAPIError, VkAuthError

V = '5.9'
login = input('Логин: ')
while True:
    password = input('Пароль: ')
    try:
        session = vk.AuthSession(6004708, login, password, 'wall')
        break
    except VkAuthError as e:
        print(e)
        print('Неверный пароль, попробуйте снова')
group = urlparse(input('Ссылка на группу: ')).path[1:]
likes_amount = input('Кол-во лайков("inf" - до конца стены)')
delay = float(input('Задержка после запросов(милисекунды, влияет на частоту капчи и скорость прохода)')) / 1000

vk_api = vk.API(session)

got = 0


def like(user_id, amount):
    off = 0
    liked = 0
    while True:
        try:
            posts = vk_api.wall.get(owner_id=user_id, offset=off, count=100, filter='owner', v=V)[u'items']
            time.sleep(delay)
            if not posts or str(liked) == amount:
                break
            else:
                count = 0
                for p in posts:
                    if count % 3 == 0:
                        vk_api.likes.add(type='post', owner_id=user_id, item_id=p[u'id'], v=V)
                        time.sleep(delay)
                        liked += 1
                    count += 1
        except VkAPIError as error:
            if error.is_captcha_needed():
                captcha_image = error.captcha_img()
                #послать img в телеграмм
                #получить из телеги ответ
                #перепослать запрос(в какой момент он происходит??)
            else:
                print(error)
        except Exception as exception:
            print(exception)


while True:
    try:
        members = vk_api.groups.getMembers(group_id=group, offset=got, count=1000, v=V)[u'items']
        time.sleep(delay)
        got += 1000
        if not members:
            print('Дело сделано')
            break
        else:
            for u_id in members:
                like(u_id, likes_amount)
    except Exception as e:
        print(e)
