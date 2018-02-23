import time
import webbrowser as wb
from urllib.parse import urlparse, parse_qsl
import os.path

import json
import vk
from vk.exceptions import VkAPIError


class WorkInformation:
    CONFIG_FILE = 'variables.cfg'
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
                print('Token not configured or broken, auth needed. Try running with \'update_token\' argument')
                quit()
            if not self.check_variables():
                print('Variables not configured or broken. Try running with \'init\' argument')
                quit()
            else:
                self.get_information_from_file()
                if self.got == 0:
                    print('Start new job.')
                else:
                    print('Continue the previous job. ' + str(self.got) + ' users are already liked')
        elif process_type == 'update vars':
            if not self.check_token():
                print('Invalid token. Firstly try running with \'update_token\' parameter')
            if not self.check_variables():
                self.get_information_from_user()
            else:
                if input('Variables are ok. Sure you want to reconfigure them? (Y/n): ').lower() != 'n':
                    self.clear_vars()
                    self.get_information_from_user()
        elif process_type == 'update token':
            while True:
                self.auth()
                if not self.check_token():
                    print('Invalid token')
                else:
                    break

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
            live_time = int(parse_dict[u'expires_in'])
            got_time = time.time()
            self.write_token(live_time, got_time)
        except KeyError:
            print('Valid token not found. Allow access for application and retry')
            quit()

    'Checkers'

    def check_token(self):
        if not os.path.exists(self.TOKEN_FILE):
            return False
        with open(self.TOKEN_FILE, 'r', encoding='utf-8') as token_file:
            try:
                token_data = json.loads(token_file.read())
                self.token = token_data['token']
                live_time = token_data['live_time']
                got_time = token_data['got_time']
            except ValueError:
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
        if not os.path.exists(self.CONFIG_FILE):
            return False
        with open(self.CONFIG_FILE, 'r', encoding='utf-8') as data_file:
            try:
                data = json.loads(data_file.read())
            except ValueError:
                return False
        return True

    'Gathering information'

    def get_group_name(self):
        while True:
            group = urlparse(input('Group link or group id: ')).path
            if group[0] == '/':
                group = group[1:]
            if input('Group ID "' + group + '", is correct? (Y/n) ').lower() != 'n':
                try:
                    self.api.groups.getMembers(group_id=group, count=1, v=self.V)
                    break
                except VkAPIError:
                    print('Non-correct group link or ID')
            else:
                print('Repeat enter group id')
        return group

    def get_information_from_user(self):
        print('\nConfigure variables:')
        self.likes_amount = int(input('Max likes on user page("-1" for infinity): '))
        self.delay = int(input('Delay between requests (seconds, small values lead to a captcha and temporary '
                               'blocking), it is recommended not less than 10 seconds: '))
        self.post_offset = int(input('The offset between the posts: '))
        self.group = self.get_group_name()
        self.got = 0
        self.write_vars()

    def get_information_from_file(self):
        with open(self.CONFIG_FILE, 'r', encoding='utf-8') as data_file:
            data = json.loads(data_file.read())
            self.likes_amount = data['likes_amount']
            self.delay = data['delay']
            self.group = data['group']
            self.got = data['got']
            self.post_offset = data['post_offset']

    'Writers'

    def write_token(self, live_time, got_time):
        with open(self.TOKEN_FILE, 'w') as token_file:
            d = {
                "token": self.token,
                "live_time": live_time,
                "got_time": got_time,
            }
            token_file.write(json.dumps(d))

    def write_vars(self):
        with open(self.CONFIG_FILE, 'w') as vars_file:
            d = {
                "likes_amount": self.likes_amount,
                "delay": self.delay,
                "group": self.group,
                "got": self.got,
                "post_offset": self.post_offset,
            }
            vars_file.write(json.dumps(d))

    def clear_vars(self):
        vars_file = open(self.CONFIG_FILE, 'w')
        vars_file.write('')
        vars_file.close()
