import time
import webbrowser as wb
from urllib.parse import urlparse, parse_qsl
import os.path

import vk
from vk.exceptions import VkAPIError


class WorkInformation:
    FILENAME = 'variables.log'
    TOKEN_FILE = 'token.log'
    V = '5.73'

    session = None
    api = None
    token = None
    likes_amount = None
    delay = None
    group = None
    got = None

    def __init__(self):
        while not self.check_token():
            self.auth()
        if not self.check_variables():
            self.get_information_from_user()
        else:
            self.get_information_from_file()

    'Authentication'

    def do_session_api(self):
        self.session = vk.Session(access_token=self.token)
        self.api = vk.API(self.session)

    def auth(self):
        print('Токена нет, или он неверный, сейчас будет регистрация')
        site = 'https://oauth.vk.com/authorize?client_id=6004708&' \
               'redirect_uri=https://oauth.vk.com/blank.html&scope=wall&response_type=token&v=5.73'
        print('ВНИМАНИЕ. Через 6 секунд откроется сайт аутентификации, не закрывайте вкладку после разрешения доступа')
        time.sleep(6)
        wb.open(site)
        try:
            parse_dict = dict(parse_qsl(urlparse(input('Введите ссылку/поле адреса открывшегося сайта: ')).fragment))
            self.token = parse_dict[u'access_token']
            live_time = parse_dict[u'expires_in']
            got_time = str(time.time())
            self.write_token(live_time, got_time)
        except KeyError:
            print('Неверный токен(не найден). Запустите заново и разрешите доступ аутентификации')
            quit()

    'Checkers'

    def check_token(self):
        if not os.path.exists(self.TOKEN_FILE):
            return False
        num_lines = sum(1 for line in open(self.TOKEN_FILE))
        if num_lines != 3:
            return False
        with open(self.TOKEN_FILE, 'r') as t:
            token = t.readline()
            self.token = token[:len(token) - 1]
            live_time = t.readline()
            live_time = int(live_time[:len(live_time) - 1])
            got_time = t.readline()
            got_time = float(got_time[: len(got_time) - 1])
            if time.time() - got_time > live_time:
                print('Токен просрочен!')
                return False
        self.do_session_api()
        try:
            self.api.users.get(user_ids=1, v=self.V)
        except VkAPIError as e:
            if e.code == 5:
                print('Токен неверный!')
            else:
                print(e)
            return False
        return True

    def check_variables(self):
        if not os.path.exists(self.FILENAME):
            return False
        continuing = True
        num_lines = sum(1 for line in open(self.FILENAME))
        with open(self.FILENAME, 'r') as log:
            if (len(log.read()) == 0) or (num_lines != 4):
                continuing = False
        return continuing

    'Gathering information'

    @staticmethod
    def get_group_name():
        while True:
            group = urlparse(input('Ссылка на группу/короткий домен/id: ')).path
            if group[0] == '/':
                group = group[1:]
            print('Домен/id группы - ', group, 'верно?(y/n)')
            ok = input().lower()
            if ok == 'y':
                break
            else:
                print('Повторите ввод группы по-другому')
        return group

    def get_information_from_user(self):
        print('Начинаем новый процесс!')
        self.likes_amount = input('Кол-во лайков("inf" - до конца стены): ')
        self.delay = float(input('Задержка после запросов(милисекунды, влияет на частоту капчи и скорость прохода,'
                                 ' рекомендую ~300-1000): ')) / 1000
        self.group = self.get_group_name()
        self.got = 0
        self.write_vars()

    def get_information_from_file(self):
        print('Запускаю продолжение процесса')
        with open(self.FILENAME, 'r') as log:
            likes_amount = log.readline()
            self.likes_amount = likes_amount[:len(likes_amount) - 1]
            delay = log.readline()
            self.delay = float(delay[:len(delay) - 1])
            group = log.readline()
            self.group = group[:len(group) - 1]
            self.got = int(log.readline())

    'Writers'

    def write_token(self, lt, gt):
        with open(self.TOKEN_FILE, 'w') as t:
            t.write(self.token + '\n')
            t.write(lt + '\n')
            t.write(gt + '\n')

    def write_vars(self):
        log = open(self.FILENAME, 'w')
        log.write(self.likes_amount + '\n')
        log.write(str(self.delay) + '\n')
        log.write(self.group + '\n')
        log.write(str(self.got) + '\n')
        log.close()

    def clear_log(self):
        log = open(self.FILENAME, 'w')
        log.write('')
        log.close()
