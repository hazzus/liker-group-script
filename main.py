import vk
import time
from urllib.parse import urlparse, parse_qsl
from urllib.request import urlopen
from PIL import Image
import webbrowser as wb

from vk.exceptions import VkAPIError

global token
global likes_amount
global delay
global group
global got
filename = 'variables.log'
V = '5.73'
COUNT = 1000

continuing = True
num_lines = sum(1 for line in open(filename))
with open(filename, 'r') as log:
    if (len(log.read()) == 0) or (num_lines != 5):
        continuing = False


def get_group():
    while True:
        group = urlparse(input('Ссылка на группу/короткий домен/id: ')).path
        if group[0] == '/':
            group = group[1:]
        print('Домен/id группы - ', group, 'верно?(y/n)')
        ok = input()
        if ok == 'y':
            break
        else:
            print('Повторите ввод группы по-другому')
    return group


if not continuing:
    print('Начинаем новый процесс!')
    site = 'https://oauth.vk.com/authorize?client_id=6004708&' \
           'redirect_uri=https://oauth.vk.com/blank.html&scope=wall&response_type=token&v=5.73'
    print('ВНИМАНИЕ. Через 6 секунд откроется сайт аутентификации, не закрывайте вкладку после разрешения доступа')
    time.sleep(6)
    wb.open(site)
    try:
        token = dict(parse_qsl(urlparse(input('Введите ссылку/поле адреса открывшегося сайта: ')).fragment))[u'access_token']
    except KeyError:
        print('Неверный токен(не найден). Запустите заново и разрешите доступ аутентификации')
        quit()
    likes_amount = input('Кол-во лайков("inf" - до конца стены): ')
    delay = float(input('Задержка после запросов(милисекунды, влияет на частоту капчи и скорость прохода,'
                        ' рекомендую ~900-1500): ')) / 1000
    group = get_group()
    got = 0
else:
    print('Запускаю продолжение процесса')
    log = open(filename, 'r')
    token = log.readline()
    token = token[:len(token) - 1]
    likes_amount = log.readline()
    likes_amount = likes_amount[:len(likes_amount) - 1]
    delay = log.readline()
    delay = float(delay[:len(delay) - 1])
    group = log.readline()
    group = group[:len(group) - 1]
    got = int(log.readline())
    log.close()

session = vk.Session(access_token=token)
vk_api = vk.API(session)


def log_write(number):
    log = open(filename, 'w')
    log.write(token + '\n')
    log.write(likes_amount + '\n')
    log.write(str(delay) + '\n')
    log.write(group + '\n')
    log.write(str(number) + '\n')
    log.close()


def clear_log():
    log = open(filename, 'w')
    log.write('')
    log.close()


def open_image(captcha_url):
    image = Image.open(urlopen(captcha_url))
    image.show()


def captcha_cover(error):
    captcha_image = error.captcha_img
    open_image(captcha_image)
    return input('Введите капчу: '), error.captcha_sid


def like(user_id, amount):
    off = 0
    liked = 0
    while True:
        posts = None
        try:
            posts = vk_api.wall.get(owner_id=user_id, offset=off, count=100, filter='owner', v=V)[u'items']
        except VkAPIError as error:
            if error.is_captcha_needed():
                captcha = captcha_cover(error)
                posts = vk_api.wall.get(owner_id=user_id, offset=off, count=100, filter='owner', v=V,
                                        captcha_sid=captcha[1], captcha_key=captcha[0])[u'items']
            elif error.code == 6:
                time.sleep(1)
                posts = vk_api.wall.get(owner_id=user_id, offset=off, count=100, filter='owner', v=V)[u'items']
            else:
                print(error)
        time.sleep(delay)
        if (not posts) or (str(liked) == amount):
            break
        else:
            count = 0
            for p in posts:
                if str(liked) == amount:
                    break
                if count % 3 == 0:

                    try:
                        vk_api.likes.add(type='post', owner_id=user_id, item_id=p[u'id'], v=V)
                    except VkAPIError as error:
                        if error.is_captcha_needed():
                            captcha = captcha_cover(error)
                            vk_api.likes.add(type='post', owner_id=user_id, item_id=p[u'id'], v=V,
                                             captcha_sid=captcha[1], captcha_key=captcha[0])
                        else:
                            print(error)
                    time.sleep(delay)
                    liked += 1
                count += 1


log_write(got)
while True:
    try:
        members = None
        try:
            members = vk_api.groups.getMembers(group_id=group, offset=got, count=COUNT, v=V)[u'items']
        except VkAPIError as error:
            if error.is_captcha_needed():
                captcha = captcha_cover(error)
                members = vk_api.groups.getMembers(group_id=group, offset=got, count=COUNT, v=V, captcha_sid=captcha[1],
                                                   captcha_key=captcha[1])[u'items']
            elif error.code == 6:
                time.sleep(1)
                members = vk_api.groups.getMembers(group_id=group, offset=got, count=COUNT, v=V)[u'items']
            elif error.code == 125:
                print('Неверный домен группы, попробуйте еще раз')
                print(group)
                group = get_group()
            else:
                print(error)
                clear_log()
                print('В логах произошла ошибка, они сброшены, перезапустите процесс')
                break
        time.sleep(delay)
        if not members:
            print('Дело сделано')
            break
        else:
            for u_id in members:
                like(u_id, likes_amount)
                got += 1
                log_write(got)
    except (KeyboardInterrupt, SystemExit) as e:
        log_write(got)
        quit()
    time.sleep(2)
