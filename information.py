import time
import webbrowser as wb
from urllib.parse import urlparse, parse_qsl
import os.path
from configparser import ConfigParser, MissingSectionHeaderError

import vk
from vk.exceptions import VkAPIError


class WorkInformation:
    FILENAME = 'variables.cfg'
    TOKEN_FILE = 'token.cfg'
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
        try:
            token_config = ConfigParser()
            token_config.read(self.TOKEN_FILE)
            self.token = token_config['TOKEN']['token']
            live_time = int(token_config['TOKEN']['live_time'])
            got_time = float(token_config['TOKEN']['got_time'])
        except (KeyError, MissingSectionHeaderError):
            return False
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
        num_lines = sum(1 for line in open(self.FILENAME))
        if num_lines != 5:
            return False
        return True

    'Gathering information'

    def get_group_name(self):
        while True:
            group = urlparse(input('Ссылка на группу/короткий домен/id: ')).path
            if group[0] == '/':
                group = group[1:]
            print('Домен/id группы - ', group, 'верно?(y/n)')
            ok = input().lower()
            if ok == 'y':
                try:
                    self.api.groups.getMembers(group_id=group, count=1, v=self.V)
                    break
                except VkAPIError:
                    print('Неверный домен/id. Попробуйте по-другому')
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
        config = ConfigParser()
        config.read(self.FILENAME)
        self.likes_amount = config['MAIN']['likes_amount']
        self.delay = float(config['MAIN']['delay'])
        self.group = config['MAIN']['group']
        self.got = int(config['MAIN']['got'])

    'Writers'

    def write_token(self, lt, gt):
        with open(self.TOKEN_FILE, 'w') as t:
            t.write('[TOKEN]\n')
            t.write('token=' + self.token + '\n')
            t.write('live_time=' + lt + '\n')
            t.write('got_time=' + gt + '\n')

    def write_vars(self):
        with open(self.FILENAME, 'w') as var_conf:
            var_conf.write('[MAIN]\n')
            var_conf.write('likes_amount=' + self.likes_amount + '\n')
            var_conf.write('delay=' + str(self.delay) + '\n')
            var_conf.write('group=' + self.group + '\n')
            var_conf.write('got=' + str(self.got) + '\n')

    def clear_log(self):
        log = open(self.FILENAME, 'w')
        log.write('')
        log.close()
