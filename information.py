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
    post_offset = None

    def __init__(self, process_type):
        if process_type == 'worker':
            if not self.check_token():
                print('Token not configured or broken, auth needed. Try running with \'init\' argument')
                quit()
            if not self.check_variables():
                print('Variables not configured or broken. Try running with \'init\' argument')
                quit()
            else:
                self.get_information_from_file()
        elif process_type == 'configurator':
            while not self.check_token():
                self.auth()
            print('Token is okay')
            if not self.check_variables():
                self.get_information_from_user()
            else:
                if input('Variables are ok. Do you want to reconfigure them?(y/n): ') == 'y':
                    self.clear_vars()
                    self.get_information_from_user()


    'Authentication'

    def do_session_api(self):
        self.session = vk.Session(access_token=self.token)
        self.api = vk.API(self.session)

    def auth(self):
        print('Starting auth process..')
        site = 'https://oauth.vk.com/authorize?client_id=6004708&' \
               'redirect_uri=https://oauth.vk.com/blank.html&scope=wall&response_type=token&v=5.73'
        print('After 6 seconds, the authentication site will open, do not close the tab after allowing access')
        time.sleep(6)
        wb.open(site)
        try:
            parse_dict = dict(parse_qsl(urlparse(input('Paste link to open page: ')).fragment))
            self.token = parse_dict[u'access_token']
            live_time = parse_dict[u'expires_in']
            got_time = str(time.time())
            self.write_token(live_time, got_time)
        except KeyError:
            print('Valid token not found. Allow access for application and retry')
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
            print('Token expired!')
            return False
        self.do_session_api()
        try:
            self.api.users.get(user_ids=1, v=self.V)
        except VkAPIError as e:
            if e.code == 5:
                print('Token is incorrect')
            else:
                print(e)
            return False
        return True

    def check_variables(self):
        if not os.path.exists(self.FILENAME):
            return False
        num_lines = sum(1 for line in open(self.FILENAME))
        if num_lines != 6:
            return False
        return True

    'Gathering information'

    def get_group_name(self):
        while True:
            group = urlparse(input('Group link or group id: ')).path
            if group[0] == '/':
                group = group[1:]
            print('Group ID ', group, ', is correct ?(y/n)')
            ok = input().lower()
            if ok == 'y':
                try:
                    self.api.groups.getMembers(group_id=group, count=1, v=self.V)
                    break
                except VkAPIError:
                    print('Non-correct group link or ID')
            else:
                print('Repeat enter group id')
        return group

    def get_information_from_user(self):
        print('Start new job. Configure:')
        self.likes_amount = input('Max likes on user page("inf" for infinity): ')
        self.delay = float(input('Delay between requests (seconds, small values lead to a captcha and temporary '
                                 'blocking), it is recommended not less than 10 seconds: '))
        self.post_offset = float(input('The offset between the posts: '))
        self.group = self.get_group_name()
        self.got = 0
        self.write_vars()

    def get_information_from_file(self):
        config = ConfigParser()
        config.read(self.FILENAME)
        self.likes_amount = config['MAIN']['likes_amount']
        self.delay = float(config['MAIN']['delay'])
        self.group = config['MAIN']['group']
        self.got = int(config['MAIN']['got'])
        self.post_offset = int(config['MAIN']['post_offset'])
        print('Continue the previous job. ' + str(self.got) + ' users are already liked')

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
            var_conf.write('post_offset=' + str(self.post_offset) + '\n')

    def clear_vars(self):
        vars_file = open(self.FILENAME, 'w')
        vars_file.write('')
        vars_file.close()
