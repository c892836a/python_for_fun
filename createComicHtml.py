import urllib.parse
import os
from os import walk
from os import system
import configparser
import re
import time
import sys
import ftputil
import dominate.tags as dmtags
from dominate.util import text
from PyQt5.QtWidgets import (QFileDialog, QAbstractItemView, QListView,
                             QTreeView, QApplication, QDialog)
from PyQt5.QtCore import QUrl
import easygui
import getLogger

# const variable
PREFERENCE_FILE = "preference_path"

# initial global variable
host = ""
user = ""
password = ""
ftp_used_size = 0
total_file_number = 0
process_file_number = 0
upload_file_number = 0

# initual logger
logger = getLogger.GetLogger("Comic", "createComicHtml").initial_logger()


def get_preference_path(config_file):
    path_list = []
    with open("./config/{}".format(config_file), "r", encoding='utf8') as f:
        for path in f:
            path_list.append(path)
    return path_list

# folder choose ui


class _getExistingDirectories(QFileDialog):
    def __init__(self, *args):
        qturl = [QUrl('file:'), QUrl(
            "file:///" + os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop'))]
        path_list = get_preference_path(PREFERENCE_FILE)
        for path in path_list:
            qturl.append(QUrl("file:///{}".format(path.strip())))
        super(_getExistingDirectories, self).__init__(*args)
        self.setOption(self.DontUseNativeDialog, True)
        self.setFileMode(self.Directory)
        self.setOption(self.ShowDirsOnly, True)
        self.findChildren(QListView)[0].setSelectionMode(
            QAbstractItemView.ExtendedSelection)
        self.findChildren(QTreeView)[0].setSelectionMode(
            QAbstractItemView.ExtendedSelection)
        # self.setDirectory(os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop'))
        self.setSidebarUrls(qturl)


def restrict_foldername(name):
    new_name = name
    if len(name.encode("utf-8")) > 126:
        new_name = str(name.encode("utf-8")[:126], "utf-8")
        logger.info("new directory name change from %s to %s",
                    name, new_name)
    return new_name


def ftp_upload(parent_dic, filepath, title, file_array):
    with ftputil.FTPHost(
            host,
            user,
            password) as ftp_host:
        global ftp_used_size, process_file_number, upload_file_number
        ftp_host.chdir("WWW")
        # length limit
        parent_dic = restrict_foldername(parent_dic)
        new_title = restrict_foldername(title)
        if parent_dic.strip() != "":
            if ftp_host.path.exists(parent_dic.encode("utf-8")):
                pass
            else:
                ftp_host.mkdir(parent_dic.encode("utf-8"))
            ftp_host.chdir(parent_dic.encode("utf-8"))
        logger.info("uploading %s.html", filepath.replace("&", "$"))
        ftp_host.upload((filepath.replace("&", "$") + ".html").encode("utf-8"),
                        (title + ".html").encode("utf-8"))
        logger.info("add directory %s", filepath)
        if ftp_host.path.exists(new_title.encode("utf-8")):
            pass
            # for _root, _dirs, files in ftp_host.walk(ftp_host.curdir):
            #     for file in files:
            #         ftp_host.remove(file)
        else:
            ftp_host.mkdir(new_title.encode("utf-8"))
        ftp_host.chdir(new_title.encode("utf-8"))
        os.chdir(filepath)
        current_file_list = ftp_host.listdir(ftp_host.curdir)
        for name in file_array:
            if name in current_file_list:
                logger.info("skipping %s ---------------- %s%%", name,
                            str(round(process_file_number * 100 / total_file_number, 1)))
                continue
            logger.info("uploading %s ---------------- %s%%", name,
                        str(round(process_file_number * 100 / total_file_number, 1)))
            ftp_host.upload(name.encode("utf-8"), name.encode("utf-8"))
            ftp_used_size += os.path.getsize(name)
            upload_file_number += 1


def ftp_singlehtml_upload(filepath, web_title):
    with ftputil.FTPHost(
            host,
            user,
            password) as ftp_host:
        ftp_host.chdir("WWW")
        logger.info("uploading %s\\%s.html", filepath, web_title)
        ftp_host.upload(("{}\\{}.html".format(filepath, web_title)).encode("utf-8"),
                        "{}.html".format(web_title).encode("utf-8"))


# def ftp_get_folder_size(folder_path):
#     with ftputil.FTPHost(
#             host,
#             user,
#             password) as ftp_host:
#         global ftp_used_size
#         now_size = 0
#         for root, _dirs, files in ftp_host.walk(folder_path):
#             for name in files:
#                 fullpath = ftp_host.path.join(root, name)
#                 now_size += ftp_host.path.getsize(fullpath)
#         logger.info("{} cost {} MB".format(folder_path, str(int(ftp_used_size / 1024 / 1024))))
#         ftp_used_size += now_size


def ftp_get_total_size():
    with ftputil.FTPHost(
            host,
            user,
            password) as ftp_host:
        global ftp_used_size
        ftp_host.chdir("WWW")
        if "totalSize" not in ftp_host.listdir(ftp_host.curdir):
            new_size = 0
            for root, _dirs, files in ftp_host.walk(ftp_host.curdir):
                for name in files:
                    fullpath = ftp_host.path.join(root, name)
                    new_size += ftp_host.path.getsize(fullpath)
            with ftp_host.open("totalSize", "w", encoding='utf8') as f:
                f.write(str(new_size))
            logger.info("this time total upload %s files, %s MB", upload_file_number,
                        str(int(ftp_used_size / 1024 / 1024)))
            ftp_used_size = new_size
        else:
            with ftp_host.open("totalSize", "r", encoding='utf8') as f:
                new_size = int(f.read())
            logger.info("this time total upload %s files, %s MB", upload_file_number,
                        str(int(ftp_used_size / 1024 / 1024)))
            ftp_used_size += new_size
        with ftp_host.open("totalSize", "w", encoding='utf8') as f:
            f.write(str(ftp_used_size))


# create html content


def create_singlepage_html(local, is_mainpage, web_title, web_title_next,
                           web_title_pre, file_array, path):
    if is_mainpage:
        os.chdir(path)
        os.chdir(os.pardir)
        parent_web_title = str(os.getcwd())[str(os.getcwd()).rindex("\\") + 1:]
    if local:
        web_title_next = web_title_next.replace("&", "$")
        web_title_pre = web_title_pre.replace("&", "$")
    _html = dmtags.html(style="background-color:black;")
    _head, _body = _html.add(dmtags.head(dmtags.title(web_title)),
                             dmtags.body())
    with _head:
        dmtags.comment("The page is genarated on {} by Ein".format(
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        dmtags.meta(charset="utf-8", name="viewport",
                    content="width=device-width, initial-scale=1")
        dmtags.link(href="https://fonts.googleapis.com/css?family=Noto+Sans+JP:500",
                    rel="stylesheet")
        dmtags.link(href="https://cdnjs.cloudflare.com/ajax/libs/fancybox/3.5.6/"
                         "jquery.fancybox.min.css",
                    rel="stylesheet")
        dmtags.link(href="https://cdnjs.cloudflare.com/ajax/libs/uikit/3.0.0-rc.25/css/"
                         "uikit.min.css",
                    rel="stylesheet")
        dmtags.link(href="https://rawcdn.githack.com/c892836a/python_for_fun/"
                         "b2fa53022b0ae5a26d6f140c38b860a210c21040/css/custom.css",
                    rel="stylesheet")
        dmtags.link(href="https://lh3.googleusercontent.com/S__tM5EYqZDFLuv1uPG" +
                    "mlZTTLLyNAbUvljzDH8-S0Pxq2nA9fnFF3SwU0w0wF8PlMu_hv3WhLMdlFodKbQ=s0",
                    rel="shortcut icon", type="image/vnd.microsoft.icon")
        dmtags.script(
            src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js")
        dmtags.script(
            src="https://cdnjs.cloudflare.com/ajax/libs/fancybox/3.5.6/jquery.fancybox.min.js")

    main_div = _body.add(dmtags.div(
        style="text-align:center; font-family: 'Noto Sans JP', sans-serif; font-size:32px;"))
    with main_div:
        _p1 = dmtags.p(style="color:#C2FFFC;padding-top: 20px;")
        if web_title_next == "" and web_title_pre == "":
            _button_top_div = dmtags.div(style="display: none;")
        else:
            _button_top_div = dmtags.div(style="padding-bottom: 30px;")
        if local:
            for pic in file_array:
                _a1 = dmtags.a(datafancybox="gallery",
                               href='./{}/{}'.format(urllib.parse.quote(web_title),
                                                     urllib.parse.quote(pic)))
                with _a1:
                    dmtags.img(width="1200px",
                               src='./{}/{}'.format(urllib.parse.quote(web_title),
                                                    urllib.parse.quote(pic)))
        else:
            web_title_temp = restrict_foldername(web_title)
            for pic in file_array:
                _a1 = dmtags.a(datafancybox="gallery",
                               href='./{}/{}'.format(urllib.parse.quote(web_title_temp),
                                                     urllib.parse.quote(pic)))
                with _a1:
                    dmtags.img(width="1200px",
                               src='./{}/{}'.format(urllib.parse.quote(web_title_temp),
                                                    urllib.parse.quote(pic)))
        with _p1:
            text("{} ({}P)".format(web_title, str(len(file_array))))
        _button_bottom_div = dmtags.div(
            style="padding-top: 20px; padding-bottom: 40px;")
        with _button_top_div:
            if web_title_pre != "":
                dmtags.a("Prev", cls="uk-button uk-button-secondary n-bt",
                         href="./{}.html".format(web_title_pre))
            else:
                dmtags.a("Prev", cls="uk-button uk-button-secondary h-bt",
                         href="./{}.html".format(web_title_pre))
            if is_mainpage:
                dmtags.a("Index", cls="uk-button uk-button-secondary n-bt",
                         href="../{}.html".format(parent_web_title))
            if web_title_next != "":
                dmtags.a("Next", cls="uk-button uk-button-secondary n-bt",
                         href="./{}.html".format(web_title_next))
            else:
                dmtags.a("Next", cls="uk-button uk-button-secondary h-bt",
                         href="./{}.html".format(web_title_next))

        with _button_bottom_div:
            if web_title_pre != "":
                dmtags.a("Prev", cls="uk-button uk-button-primary n-bt",
                         href="./{}.html".format(web_title_pre))
            else:
                dmtags.a("Prev", cls="uk-button uk-button-primary h-bt",
                         href="./{}.html".format(web_title_pre))
            if is_mainpage:
                dmtags.a("Index", cls="uk-button uk-button-primary n-bt",
                         href="../{}.html".format(parent_web_title))
            if web_title_next != "":
                dmtags.a("Next", cls="uk-button uk-button-primary n-bt",
                         href="./{}.html".format(web_title_next))
            else:
                dmtags.a("Next", cls="uk-button uk-button-primary h-bt",
                         href="./{}.html".format(web_title_next))

    # create html file
    with open("{}.html".format(path).replace("&", "$"), "w", encoding='utf8') as f:
        f.write("<!DOCTYPE html>\n")
        f.write(_html.render().replace("datafancybox", "data-fancybox"))


def create_mainpage_html(url_list, path, web_title):
    _html = dmtags.html(style="background-color:#fcfbeb;")
    _head, _body = _html.add(dmtags.head(dmtags.title(web_title)),
                             dmtags.body(cls="main_page"))
    with _head:
        dmtags.comment("The page is genarated on {} by Ein".format(
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        dmtags.meta(charset="utf-8", name="viewport",
                    content="width=device-width, initial-scale=1")
        dmtags.link(href="https://fonts.googleapis.com/css?family=Noto+Sans+JP:500",
                    rel="stylesheet")
        dmtags.link(href="https://cdnjs.cloudflare.com/ajax/libs/milligram/1.3.0/milligram.min.css",
                    rel="stylesheet")
        dmtags.link(href="https://rawcdn.githack.com/c892836a/python_for_fun/"
                         "b2fa53022b0ae5a26d6f140c38b860a210c21040/css/custom.css",
                    rel="stylesheet")
        dmtags.link(href="https://lh3.googleusercontent.com/S__tM5EYqZDFLuv1uPG" +
                    "mlZTTLLyNAbUvljzDH8-S0Pxq2nA9fnFF3SwU0w0wF8PlMu_hv3WhLMdlFodKbQ=s0",
                    rel="shortcut icon", type="image/vnd.microsoft.icon")
    main_div = _body.add(dmtags.div(
        style="text-align:center; font-family: 'Noto Sans JP', sans-serif; font-size:36px;"))

    with main_div:
        _p1 = dmtags.p(style="color:#470000;")
        for url in url_list:
            _p2 = dmtags.p(style="font-size:20px;")
            with _p2:
                dmtags.a(url[0], href="{}".format(url[1]))
        with _p1:
            text("{}".format(web_title))

    # create html file
    with open("{}\\{}.html".format(path, web_title), "w", encoding='utf8') as f:
        f.write("<!DOCTYPE html>\n")
        f.write(_html.render())


def create_all_html(local, is_mainpage, path_list, webtitle_list, file_array_list):
    for i, element in enumerate(path_list):
        if i == 0 and len(path_list) == 1:
            create_singlepage_html(local, is_mainpage, webtitle_list[i], "", "",
                                   file_array_list[i], element)
        elif i == 0:
            create_singlepage_html(local, is_mainpage, webtitle_list[i], webtitle_list[i+1],
                                   "", file_array_list[i], element)
        elif i == (len(path_list) - 1):
            create_singlepage_html(local, is_mainpage,
                                   webtitle_list[i], "", webtitle_list[i-1],
                                   file_array_list[i], element)
        else:
            create_singlepage_html(local, is_mainpage, webtitle_list[i], webtitle_list[i+1],
                                   webtitle_list[i-1], file_array_list[i], element)


# format filename to sort correctly
def format_filename(name):
    f_name = name.split('.')[0]
    if f_name.isdigit():
        return "{:03d}".format(int(f_name))
    return f_name


def main():
    global host, user, password, total_file_number

    # initual ftp user data
    config = configparser.ConfigParser()
    config.read('./config/config_comic.ini')
    host = config.get("FTP", "host")
    user = config.get("FTP", "user")
    password = config.get("FTP", "password")

    # choose directory
    _qapp = QApplication(sys.argv)
    dlg = _getExistingDirectories()
    webtitle_list = []
    if dlg.exec_() == QDialog.Accepted:
        path_list = dlg.selectedFiles()
        for path in path_list:
            webtitle_list.append(path[path.rindex('/') + 1:])
    else:
        return

    # get file list in directory
    file_array_list = []
    regex = re.compile(r'.+\.(jpg|jpeg|bmp|png|webp)')
    for path in path_list:
        file_array = []
        for (_dirpath, _dirnames, filenames) in walk(path):
            filenames_temp = []
            for f in sorted(filenames, key=lambda x: format_filename(x)):
                if re.search(regex, f):
                    filenames_temp.append(f)
                    total_file_number += 1
            file_array.extend(filenames_temp)
            break
        file_array_list.append(file_array)

    # do some action
    choices = ["Open Html on Browser", "Upload to FTP",
               "Open Html & Upload to FTP", "Upload to FTP & Create a main page", "Exit"]
    choise_action = easygui.choicebox("Create .html file successfully \
        \n\nNext action?", "createComicHtml", choices)
    result_url = ""
    cmd = ""
    if choise_action == "Open Html on Browser":
        time_start = time.time()
        create_all_html(True, False, path_list, webtitle_list, file_array_list)
        for path in path_list:
            if cmd == "":
                cmd = "start  \"\" \"{}.html\"".format(path.replace("&", "$"))
            else:
                cmd += " & start  \"\" \"{}.html\"".format(
                    path.replace("&", "$"))
        logger.info("command: %s", cmd)
        system("start cmd /c \"{}\"".format(cmd))
        time_spent = time.strftime(
            "%H hours, %M minunts, %S seconds", time.gmtime(time.time() - time_start))
        logger.info("spent time: %s", time_spent)

    elif choise_action == "Upload to FTP":
        time_start = time.time()
        create_all_html(False, False, path_list,
                        webtitle_list, file_array_list)
        for i, element in enumerate(path_list):
            ftp_upload("", element, webtitle_list[i], file_array_list[i])
            logger.info("remove file %s.html", webtitle_list[i])
            result_url += "{}\r\nhttp://{}/~{}/{}.html\r\n\r\n".format(
                webtitle_list[i], host, user, urllib.parse.quote(webtitle_list[i]))
            logger.info(webtitle_list[i])
            logger.info("http://%s/~%s/%s.html", host, user,
                        urllib.parse.quote(webtitle_list[i]))
            os.remove("{}.html".format(element.replace("&", "$")))
        logger.info("checking ftp used size")
        ftp_get_total_size()
        time_spent = time.strftime(
            "%H hours, %M minunts, %S seconds", time.gmtime(time.time() - time_start))
        logger.info("FTP user %s used %s MB", user,
                    str(int(ftp_used_size / 1024 / 1024)))
        logger.info("spent time: %s", time_spent)
        result_url += "FTP user {} used {} MB\r\n".format(
            user, str(int(ftp_used_size / 1024 / 1024)))
        result_url += "spent time: {}".format(time_spent)
        easygui.codebox(text=result_url.strip(),
                        title="Create Html Url", msg="Copy the url")

    elif choise_action == "Open Html & Upload to FTP":
        time_start = time.time()
        cmd = ""
        create_all_html(False, False, path_list,
                        webtitle_list, file_array_list)
        for i, element in enumerate(path_list):
            if cmd == "":
                cmd = "start \"\" \"{}.html\"".format(
                    element.replace("&", "$"))
            else:
                cmd += "& start \"\" \"{}.html\"".format(
                    element.replace("&", "$"))
            ftp_upload("", element, webtitle_list[i], file_array_list[i])
            logger.info("remove file %s.html", webtitle_list[i])
            result_url += "{}\r\nhttp://{}/~{}/{}.html\r\n\r\n".format(
                webtitle_list[i], host, user, urllib.parse.quote(webtitle_list[i]))
            logger.info(webtitle_list[i])
            logger.info("http://%s/~%s/%s.html", host, user,
                        urllib.parse.quote(webtitle_list[i]))
            os.remove("{}.html".format(element.replace("&", "$")))
        create_all_html(True, False, path_list, webtitle_list, file_array_list)
        system("start cmd /c \"{}\"".format(cmd))
        logger.info("checking ftp used size")
        ftp_get_total_size()
        time_spent = time.strftime(
            "%H hours, %M minunts, %S seconds", time.gmtime(time.time() - time_start))
        logger.info("FTP user %s used %s MB", user,
                    str(int(ftp_used_size / 1024 / 1024)))
        logger.info("spent time: %s", time_spent)
        result_url += "FTP user {} used {} MB\r\n".format(
            user, str(int(ftp_used_size / 1024 / 1024)))
        result_url += "spent time: {}".format(time_spent)
        easygui.codebox(text=result_url.strip(),
                        title="Create Html Url", msg="Copy the url")

    elif choise_action == "Upload to FTP & Create a main page":
        time_start = time.time()
        url_list = []
        create_all_html(False, True, path_list, webtitle_list, file_array_list)
        os.chdir(path_list[0])
        os.chdir(os.pardir)
        web_title = str(os.getcwd())[str(os.getcwd()).rindex("\\") + 1:]
        for i, element in enumerate(path_list):
            ftp_upload(web_title, element,
                       webtitle_list[i], file_array_list[i])
            map_list = [webtitle_list[i], "http://{}/~{}/{}/{}.html".format(
                host, user, web_title, urllib.parse.quote(webtitle_list[i]))]
            url_list.append(map_list)
            os.remove("{}.html".format(element.replace("&", "$")))
        create_mainpage_html(url_list, os.getcwd(), web_title)
        ftp_singlehtml_upload(os.getcwd(), web_title)
        os.remove("{}\\{}.html".format(os.getcwd(), web_title))
        logger.info("checking ftp used size")
        ftp_get_total_size()
        time_spent = time.strftime(
            "%H hours, %M minunts, %S seconds", time.gmtime(time.time() - time_start))
        result_url += "{}\r\nhttp://{}/~{}/{}.html\r\n\r\n".format(
            web_title, host, user, urllib.parse.quote(web_title))
        logger.info(web_title)
        logger.info("http://%s/~%s/%s.html", host,
                    user, urllib.parse.quote(web_title))
        result_url += "FTP user {} used {} MB\r\n".format(
            user, str(int(ftp_used_size / 1024 / 1024)))
        result_url += "spent time: {}".format(time_spent)
        logger.info("FTP user %s used %s MB", user,
                    str(int(ftp_used_size / 1024 / 1024)))
        logger.info("spent time: %s", time_spent)
        easygui.codebox(text=result_url.strip(),
                        title="Create a main page", msg="Copy the url")

    elif choise_action == "Exit":
        time_start = time.time()
        create_all_html(True, False, path_list, webtitle_list, file_array_list)
        time_spent = time.strftime(
            "%H hours, %M minunts, %S seconds", time.gmtime(time.time() - time_start))
        logger.info("spent time: %s", time_spent)

    else:
        pass


if __name__ == "__main__":
    main()
