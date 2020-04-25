import json
import os

USER_INFO_FILE = 'UserInfo.json'


def get_stored_username_and_key():
    """如果存储了用户名和密码，就获取它"""
    filename = USER_INFO_FILE
    try:
        with open(filename) as f_obj:
            c = json.load(f_obj)
            username = c[0]['username']
            password = c[0]['password']
    except FileNotFoundError:
        return False, False
    else:
        return username, password


def greet_user():
    """尝试初始化并访问用户数据，若存在则显示，否则询问"""
    if os.path.exists(USER_INFO_FILE):
        if input('{} 中似乎保存过登录信息，重置[y]或跳过_'.format(USER_INFO_FILE)) in ['y', 'Y']:
            os.remove('UserInfo.json')
        else:
            pass
    else:
        pass
    username, password = get_stored_username_and_key()[0], get_stored_username_and_key()[1]
    if username and password:
        return username, password
    else:
        username, password = input("请输入您的用户名："), input("请输入您的密码：")
        context = [{"username": username, "password": password}]
        with open(USER_INFO_FILE, 'w') as f_obj:
            json.dump(context, f_obj)
            print("您的登录信息已保存在 {}".format(USER_INFO_FILE))
        return username, password
