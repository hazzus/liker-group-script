import time
from urllib.request import urlopen
from PIL import Image
from requests.exceptions import ReadTimeout, ConnectionError

from vk.exceptions import VkAPIError
from information import WorkInformation

COUNT = 1000

global info


def open_image(captcha_url):
    image = Image.open(urlopen(captcha_url))
    image.show()


def captcha_cover(error):
    print(error)
    open_image(error.captcha_img)
    'webbrowser.open(error.captcha_img)'
    return input('Введите капчу: '), error.captcha_sid


def like(user_id, amount):
    off = 0
    liked = 0
    while True:
        posts = None
        try:
            posts = info.api.wall.get(owner_id=user_id, offset=off, count=100, filter='owner', v=info.V)[u'items']
        except VkAPIError as error:
            if error.is_captcha_needed():
                while True:
                    try:
                        captcha = captcha_cover(error)
                        posts = info.api.wall.get(owner_id=user_id, offset=off, count=100, filter='owner', v=info.V,
                                                  captcha_sid=captcha[1], captcha_key=captcha[0])[u'items']
                        break
                    except VkAPIError as e:
                        if e.is_captcha_needed():
                            time.sleep(info.delay)
                        else:
                            print(e)
                            print('Непредвиденная ошибка')
                            quit()
            elif error.code == 6:
                print('Слишком много запросов, подождем 1 секунду...')
                time.sleep(1)
                posts = info.api.wall.get(owner_id=user_id, offset=off, count=100, filter='owner', v=info.V)[u'items']
            elif error.code == 18:
                print('Пользователь ' + str(user_id) + ' был удален')
            else:
                print(error)
        time.sleep(info.delay)
        if (not posts) or (str(liked) == amount):
            break
        else:
            count = 0
            for p in posts:
                if str(liked) == amount:
                    break
                if count % 3 == 0:
                    print('Лайкаю пост ' + str(p[u'id']) + ' пользователя https://vk.com/id' + str(user_id))
                    try:
                        info.api.likes.add(type='post', owner_id=user_id, item_id=p[u'id'], v=info.V)
                    except VkAPIError as error:
                        if error.is_captcha_needed():
                            while True:
                                try:
                                    captcha = captcha_cover(error)
                                    info.api.likes.add(type='post', owner_id=user_id, item_id=p[u'id'], v=info.V,
                                                       captcha_sid=captcha[1], captcha_key=captcha[0])
                                    break
                                except VkAPIError as e:
                                    if e.is_captcha_needed():
                                        time.sleep(info.delay)
                                    else:
                                        print(e)
                                        print('Непредвиденная ошибка')
                                        quit()
                        elif error.code == 6:
                            print('Слишком много запросов, подождем 1 секунду..')
                            time.sleep(1)
                            info.api.likes.add(type='post', owner_id=user_id, item_id=p[u'id'], v=info.V)
                        else:
                            print(error)
                    time.sleep(info.delay)
                    liked += 1
                count += 1


def work():
    while True:
        members = None
        try:
            members = info.api.groups.getMembers(group_id=info.group, offset=info.got,
                                                 count=COUNT, v=info.V)[u'items']
        except VkAPIError as error:
            if error.is_captcha_needed():
                while True:
                    try:
                        captcha = captcha_cover(error)
                        members = \
                            info.api.groups.getMembers(group_id=info.group, offset=info.got, count=COUNT, v=info.V,
                                                       captcha_sid=captcha[1],
                                                       captcha_key=captcha[0])[u'items']
                        break
                    except VkAPIError as e:
                        if e.is_captcha_needed():
                            time.sleep(info.delay)
                        else:
                            print(e)
                            print('Непредвиденная ошибка')
                            quit()
            elif error.code == 6:
                print('Слишком много запросов, подождем 1 секунду..')
                time.sleep(1)
                members = info.api.groups.getMembers(group_id=info.group, offset=info.got,
                                                     count=COUNT, v=info.V)[u'items']
            elif error.code == 125:
                print('Неверный домен группы - ' + info.group + ', попробуйте еще раз')
                info.group = info.get_group_name()
                info.write_vars()
                members = info.api.groups.getMembers(group_id=info.group, offset=info.got,
                                                     count=COUNT, v=info.V)[u'items']
            else:
                print(error)
        time.sleep(info.delay)
        if not members:
            print('Дело сделано')
            break
        else:
            for u_id in members:
                like(u_id, info.likes_amount)
                info.got += 1
                info.write_vars()
        time.sleep(2)


if __name__ == '__main__':
    try:
        info = WorkInformation()
        work()
    except ReadTimeout:
        print('Интернет-соединение прервано')
        if info is not None:
            info.write_vars()
    except ConnectionError:
        print('Интернет соединение не установлено')
    except (KeyboardInterrupt, SystemExit):
        if info is not None:
            info.write_vars()
        print('Процесс прерван пользователем, промежуточный результат сохранен')
