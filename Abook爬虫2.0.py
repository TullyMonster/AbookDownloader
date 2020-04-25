import os
import json
import random
import re
import time
import requests as req
import user_info as u

session = req.Session()
COURSES_INFO_FILE = 'CoursesInfo.json'
courses_list = []
course_data = {}
course_tree = []
target_course_serial, target_course_id, target_course_title = '', '', ''
COURSE_INFO_FILE = ''
FILE_SAVE_ROOT_PATH = ''


def validate_title(title):
    illegal_character = r"[\ ]"  # 空格
    new_title = re.sub(illegal_character, "_", title)  # 替换为下划线
    return new_title


def try_login():
    """尝试登录，返回登录信息"""
    user_info = u.greet_user()
    Login_URL = "http://abook.hep.com.cn/loginMobile.action"  # 请求登录
    Check_Login_URL = "http://abook.hep.com.cn/verifyLoginMobile.action"  # 检查登录状态
    login_data = {'loginUser.loginName': user_info[0], 'loginUser.loginPassword': user_info[1]}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362'}
    session.post(url=Login_URL, data=login_data, headers=headers)
    print(":D 登录成功，你好 [{}] ！".format(user_info[0])
          if session.post(Check_Login_URL).json()['message'] == '已登录'
          else ":-( 用户 [{} - {}] 登录失败，请检查登录信息。".format(user_info[0], user_info[1]))


def try_get_info(data_file, renew, load):
    """检查并询问是否需要从 Abook 更新课程数据并加载"""
    if os.path.exists(data_file):  # 存在 -> 更新/使用旧文件后直接加载
        if input('{} 中保存的课程数据可能已过期，重载网络更新[y]或跳过_'.format(data_file)) in ['y']:  # 更新旧文件并加载
            eval(renew)
        else:  # 直接加载旧文件
            eval(load)
    else:  # 不存在 -> 下载最新并加载
        eval(renew)


def renew_courses_info():
    """从 Abook 获取课程信息并写入 json"""
    Courses_Info_URL = "http://abook.hep.com.cn/selectMyCourseList.action?mobile=true&cur=1"  # 获取全部课程信息
    with open(COURSES_INFO_FILE, 'w') as f_obj:
        json.dump(session.get(Courses_Info_URL).json(), f_obj, ensure_ascii=False, indent=4)
    print(':D 已完成课程信息的写入 [{}]'.format(COURSES_INFO_FILE))
    load_courses_info()


def load_courses_info():
    """从本地加载课程信息并生成列表"""
    with open(COURSES_INFO_FILE, 'r') as courses:
        courses_data: list = json.load(courses)[0]['myMobileCourseList']  # 返回全部课程字典
        print('您一共购买并绑定了 {} 门课程：'.format(len(courses_data)))
        for i in range(len(courses_data)):
            c_title = eval('courses_data[{}]'.format(i))['courseTitle']
            c_id = eval('courses_data[{}]'.format(i))['courseInfoId']
            print('{}. {}'.format(i + 1, c_title))
            courses_list.append({'serial': i + 1, 'c_id': c_id, 'c_title': c_title})


def enter_the_course():
    global target_course_serial, target_course_id, target_course_title
    raw_serial = input('输入您要加载的课程序号_')
    if raw_serial in ['1', '2', '3']:
        raw_true_serial = raw_serial
        target_course_serial = eval(raw_true_serial)
        for dic in courses_list:
            serial = 0
            if dic['serial'] == target_course_serial:
                target_course_id = dic['c_id']
                target_course_title = dic['c_title']
            else:
                serial += 1
        return target_course_serial, target_course_id, target_course_title
    else:
        enter_the_course()


def renew_course_info():
    Course_Contents_Structure_URL = 'http://abook.hep.com.cn/resourceStructure.action' \
                                    '?courseInfoId={}'.format(target_course_id)  # 获取课程章节信息
    global COURSE_INFO_FILE
    COURSE_INFO_FILE = target_course_title + '.json'
    with open(COURSE_INFO_FILE, 'w') as f_obj:
        json.dump(session.post(Course_Contents_Structure_URL).json(), f_obj, ensure_ascii=False, indent=4)
        os.system("cls")
        print(':D 已完成 [{}. {}] 的章节信息加载 [{}]'.format(target_course_serial, target_course_title, COURSE_INFO_FILE))
    load_course_info()


def create_directory():
    global FILE_SAVE_ROOT_PATH
    FILE_SAVE_ROOT_PATH = os.path.join(os.path.expanduser("~"), r'Desktop\{}'.format(target_course_title))
    try:
        os.listdir(validate_title(FILE_SAVE_ROOT_PATH))
    except FileNotFoundError:
        os.makedirs(validate_title(FILE_SAVE_ROOT_PATH))
    for item in course_tree:
        piece = item['piece']
        try:
            os.makedirs(validate_title(FILE_SAVE_ROOT_PATH + r'\{}'.format(item['name'])))
            for p in piece:
                os.makedirs(validate_title(FILE_SAVE_ROOT_PATH + r'\{}\{}'.format(item['name'], p['name'])))
        except FileExistsError:
            pass


def load_course_info():
    global course_data, course_tree
    with open(COURSE_INFO_FILE, 'r') as tree:
        course_data = json.load(tree)
        trunk = 0
        for item in course_data:
            if item['pId'] == 0:  # 5 为章节点
                t = {'pId': 0, 'name': item['name'], 'id': item['id'], 'piece': []}
                for i in course_data:
                    if i['pId'] == item['id']:
                        piece = {'id': i['id'], 'pId': i['pId'], 'name': i['name'], 'type': i['type']}
                        t['piece'].append(piece)
                course_tree.append(t)
                trunk += 1
        print('本课程共 {} 个章节\n是否更新各章节的必要信息，'.format(trunk), end='')
        create_directory()


def enter_the_chapter():
    if input('跳过[t]或继续_') in ['t', 'T']:
        pass
    else:
        for item in course_tree:  # 获得章节分类单元中的多个文件
            name_item2 = item['name']

            if item['piece']:
                for item3 in item['piece']:
                    id_item3 = item3['id']
                    name_item3 = item3['name']
                    with open(validate_title(FILE_SAVE_ROOT_PATH + r'\{}\{}\{}.json'.format(
                            name_item2, name_item3, name_item3)), 'w') as f_obj:
                        Course_Get_Resource_Info_URL = 'http://abook.hep.com.cn/courseResourceList.action' \
                                                       '?courseInfoId={}&treeId={}&cur=1'
                        json.dump(session.get(Course_Get_Resource_Info_URL.format(target_course_id, id_item3)).json(),
                                  f_obj, ensure_ascii=False, indent=4)
                        time.sleep(random.randint(2, 6))
                    print((':D 已完成 {}/{} 下载信息的写入'.format(validate_title(name_item2), validate_title(name_item3))))
            else:
                with open(validate_title(FILE_SAVE_ROOT_PATH + r'\{}\{}.json'.format(name_item2, name_item2)),
                          'w') as f_obj:
                    Course_Get_Resource_Info_URL = 'http://abook.hep.com.cn/courseResourceList.action' \
                                                   '?courseInfoId=0&treeId={}&cur=1'
                    json.dump(session.get(Course_Get_Resource_Info_URL.format(item['id'])).json(),
                              f_obj, ensure_ascii=False, indent=4)
                    time.sleep(random.randint(2, 7))
                    print(':D 已完成 {} 下载信息的写入'.format(validate_title(name_item2)))


def download():
    for current, subfolder, file in os.walk(FILE_SAVE_ROOT_PATH):
        if file:
            download_json_path = current + "\\" + file[0]
            with open(download_json_path, 'r') as dj:
                try:
                    ResourceList = json.load(dj)[0]['myMobileResourceList']  # 这是含多个字典的列表
                    # 依次取出 ID、文件名、文件类型、大小
                    for i in range(len(ResourceList)):
                        resourceInfoId = ResourceList[i]['resourceInfoId']
                        resTitle = validate_title(ResourceList[i]['resTitle'])
                        style = ResourceList[i]['resFileUrl'][ResourceList[i]['resFileUrl'].find('.'):]
                        resSize = ResourceList[i]['myresSize']
                        # print("{} {}{}({}, {})".format(current, resTitle, style, resourceInfoId, resSize), end='\n\n')
                        if style[1:] in ["wmv", "asf", "asx", "rm", "mvb", "mp4", "3gp", "mov", "m4v", "avi", "dat",
                                         "mkv", "flv", "vob"]:
                            print(r'放弃保存 ({}) {}\{}{}'.format(resSize, current, resTitle, style))
                            pass
                        else:
                            resource_request_URL = "http://abook.hep.com.cn/downLoadResouce.action?resourceInfoId={}"
                            resource_request = session.get(resource_request_URL.format(resourceInfoId))
                            print(r'保存 ({}) {}\{}{}'.format(resSize, current, resTitle, style))
                            with open(current + '\\' + resTitle + style, 'wb')as f:
                                f.write(resource_request.content)
                            time.sleep(random.randint(5, 15))
                except:
                    pass

        else:
            pass


if __name__ == '__main__':
    try_login()  # 尝试登录
    try_get_info(COURSES_INFO_FILE, 'renew_courses_info()', 'load_courses_info()')  # 拉取课程数据
    enter_the_course()  # 进入需要下载的课程，写入课程章节信息
    try_get_info(COURSE_INFO_FILE, 'renew_course_info()', 'load_course_info()')  # 拉取章节数据
    enter_the_chapter()  # 分别访问各章节返回与资源链接有关的数据
    download()  # 读取返回的资源数据，启动下载
    print("下载已完成，您可稍后删除一般无用的 .json 文件")
