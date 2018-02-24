import time
from urllib.request import urlopen
from PIL import Image
from requests.exceptions import ReadTimeout, ConnectionError
import sys

from vk.exceptions import VkAPIError
from information import WorkInformation

COUNT = 1000

global info


def open_image(captcha_url):
    image = Image.open(urlopen(captcha_url))
    image.show()


def captcha_cover(error):
    # TODO normal single method for captcha cover with constructor from error answer and eval()
    print(error)
    open_image(error.captcha_img)
    'webbrowser.open(error.captcha_img)'
    return input('Enter captcha text: '), error.captcha_sid


def like(user_id, user_info, amount):
    off = 0
    liked = 0
    if 'screen_name' in user_info.keys():
        link = user_info[u'screen_name']
    else:
        link = 'id' + str(user_id)
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
                            print('Unhandled error')
                            quit()
            elif error.code == 6:
                print('Too many requests, wait 1 seconds')
                time.sleep(1)
                posts = info.api.wall.get(owner_id=user_id, offset=off, count=100, filter='owner', v=info.V)[u'items']
            elif error.code == 18:
                print('User https://vk.com/' + link + ' has been deleted or blocked')
            else:
                print(error)
        time.sleep(info.delay)
        off += 100
        if (not posts) or (liked == amount):
            break
        else:
            count = 0
            for p in posts:
                if liked == amount:
                    break
                if count % info.post_offset == 0:
                    print('Post ' + str(p[u'id']) + ' user https://vk.com/' + link + ' ('
                          + user_info[u'first_name'] + ' ' + user_info[u'last_name'] + ') has been liked.')
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
                                        print('Unhandled error')
                                        quit()
                        elif error.code == 6:
                            print('Too many requests, wait 1 second')
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
                                                 count=COUNT, v=info.V)
        except VkAPIError as error:
            if error.is_captcha_needed():
                while True:
                    try:
                        captcha = captcha_cover(error)
                        members = \
                            info.api.groups.getMembers(group_id=info.group, offset=info.got, count=COUNT, v=info.V,
                                                       captcha_sid=captcha[1],
                                                       captcha_key=captcha[0])
                        break
                    except VkAPIError as e:
                        if e.is_captcha_needed():
                            time.sleep(info.delay)
                        else:
                            print(e)
                            print('Unhandled error')
                            quit()
            elif error.code == 6:
                print('Too many requests, wait 1 second')
                time.sleep(1)
                members = info.api.groups.getMembers(group_id=info.group, offset=info.got,
                                                     count=COUNT, v=info.V)
            elif error.code == 125:
                print('Non-valid group name: ' + info.group)
                info.group = info.get_group_name()
                info.write_vars()
                members = info.api.groups.getMembers(group_id=info.group, offset=info.got,
                                                     count=COUNT, v=info.V)
            else:
                print(error)
        time.sleep(info.delay)
        if not members[u'items']:
            print('All users liked')
            break
        else:
            all_users = members[u'count']
            user_names = info.api.users.get(user_ids=members[u'items'], fields='screen_name', v=info.V)
            for i in range(len(members[u'items'])):
                u_id = members[u'items'][i]
                u_info = user_names[i]
                like(u_id, u_info, info.likes_amount)
                info.got += 1
                info.write_vars()
                print('User http://vk.com/id' + str(u_id) + ' posts were liked. Totally ' + str(info.got) +
                      ' users liked (' + str(round(info.got / all_users * 100, 2)) + '%)')
        time.sleep(2)


def update_variables():
    try:
        WorkInformation('initial')
        print('Configures currently saved. You can now run without argument')
    except KeyboardInterrupt:
        print('\nProcess of configure interrupted by user')


def update_token():
    try:
        WorkInformation('update token')
        print('Re-auth finished successfully')
    except KeyboardInterrupt:
        print('\nAuth interrupted by user')


def debug_mode(user_links):
    pass
    # TODO Implement the debug mode


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'init':
        update_variables()
    elif len(sys.argv) == 2 and sys.argv[1] == 'update_token':
        update_token()
    elif len(sys.argv) > 2 and sys.argv[1] == 'debug':
        debug_mode(sys.argv[2:])
    elif len(sys.argv) == 1:
        info = WorkInformation('worker')
        try:
            work()
        except ReadTimeout:
            print('Timeout (connection broken)')
            if info is not None:
                info.write_vars()
        except ConnectionError:
            print('Connection not established')
        except (KeyboardInterrupt, SystemExit):
            if info is not None:
                info.write_vars()
            print('\nProcess interrupted, current state saved')
    else:
        print('Invalid argument usage')
