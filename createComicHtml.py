import easygui
import ftputil
import os
import urllib.parse
from os import walk
from os import system
import dominate.tags as dmtags
from dominate.util import text
import sys
from PyQt5.QtWidgets import (QFileDialog, QAbstractItemView, QListView,
                             QTreeView, QApplication, QDialog)
from PyQt5.QtCore import QUrl



# FTP upload function

ftp_used_size = 0


class getExistingDirectories(QFileDialog):
    def __init__(self, *args):
        qturl = [QUrl('file:'), QUrl(
            "file:///" + os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop'))]
        super(getExistingDirectories, self).__init__(*args)
        self.setOption(self.DontUseNativeDialog, True)
        self.setFileMode(self.Directory)
        self.setOption(self.ShowDirsOnly, True)
        self.findChildren(QListView)[0].setSelectionMode(
            QAbstractItemView.ExtendedSelection)
        self.findChildren(QTreeView)[0].setSelectionMode(
            QAbstractItemView.ExtendedSelection)
        # self.setDirectory(os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop'))
        self.setSidebarUrls(qturl)


def ftp_upload(filepath, title, file_array):
    with ftputil.FTPHost(
            host,
            user,
            password) as ftp_host:
        ftp_host.chdir("WWW")
        print("uploading " + filepath + ".html")
        ftp_host.upload((filepath + ".html").encode("utf-8"),
                        (title + ".html").encode("utf-8"))
        print("add directory " + filepath)
        if ftp_host.path.exists(title.encode("utf-8")):
            ftp_host.chdir(title.encode("utf-8"))
            for _root, _dirs, files in ftp_host.walk(ftp_host.curdir):
                for file in files:
                    ftp_host.remove(file)
        else:
            ftp_host.mkdir(title.encode("utf-8"))
            ftp_host.chdir(title.encode("utf-8"))
        os.chdir(filepath)
        for name in file_array:
            print("uploading " + name)
            ftp_host.upload(name.encode("utf-8"), name.encode("utf-8"))
        for root, _dirs, files in ftp_host.walk("/WWW"):
            global ftp_used_size
            for name in files:
                fullpath = ftp_host.path.join(root, name)
                ftp_used_size += ftp_host.path.getsize(fullpath)


# create html content


def create_html(web_title, file_array, path):
    _html = dmtags.html()
    _head, _body = _html.add(dmtags.head(dmtags.title(web_title)),
                             dmtags.body(style="background-color:black;"))
    with _head:
        dmtags.meta(charset="utf-8")
        dmtags.link(href="https://fonts.googleapis.com/css?family=M+PLUS+1p:500",
                    rel="stylesheet")
        dmtags.link(href="https://lh3.googleusercontent.com/S__tM5EYqZDFLuv1uPG" +
                    "mlZTTLLyNAbUvljzDH8-S0Pxq2nA9fnFF3SwU0w0wF8PlMu_hv3WhLMdlFodKbQ=s0",
                    rel="shortcut icon", type="image/vnd.microsoft.icon")

    main_div = _body.add(dmtags.div(style="text-align:center; \
        font-family: 'M PLUS 1p', sans-serif; font-size:32px;"))
    with main_div:
        _p1 = dmtags.p(style="color:#C2FFFC;")
        for pic in file_array:
            dmtags.img(width="1200px", src='./{}/{}'.format(web_title, pic))
        with _p1:
            text("{} ({}P)".format(web_title, str(len(file_array))))

    # create html file
    with open(path + ".html", "w", encoding='utf8') as f:
        f.write("<!DOCTYPE html>\n")
        f.write(_html.render())


def main():
    # choose directory
    _qapp = QApplication(sys.argv)
    dlg = getExistingDirectories()
    webtitle_list = []
    if dlg.exec_() == QDialog.Accepted:
        path_list = dlg.selectedFiles()
        for path in path_list:
            webtitle_list.append(path[path.rindex('/') + 1:])
    else:
        return

    # get file list in directory
    file_array_list = []
    for path in path_list:
        file_array = []
        for (_dirpath, _dirnames, filenames) in walk(path):
            file_array.extend(filenames)
            break
        file_array_list.append(file_array)

    # create html content
    for i in range(len(path_list)):
        create_html(webtitle_list[i], file_array_list[i], path_list[i])

    # do some action
    choices = ["Open Html on Browser", "Upload to FTP",
               "Open Html & Upload to FTP", "Exit"]
    choise_action = easygui.choicebox("Create " + path + ".html successfully \
        \n\nNext action?", "createComicHtml", choices)
    result_url = ""
    if choise_action == "Open Html on Browser":
        for path in path_list:
            cmd = "start " + path[:path.index('/') + 1] + "\"" +\
                path[path.index('/') + 1:] + ".html\""
            system("start cmd /c \"" + cmd + "\"")

    elif choise_action == "Upload to FTP":
        for i in range(len(path_list)):
            ftp_upload(path_list[i], webtitle_list[i], file_array_list[i])
            print("remove file " + webtitle_list[i] + ".html")
            result_url += "{}\nhttp://{}/~{}/{}.html\n\n".format(
                webtitle_list[i], host, user, urllib.parse.quote(webtitle_list[i]))
            result_url += "FTP user {} used {} MB".format(
                user, str(int(ftp_used_size / 1024 / 1024)))
            os.remove(path_list[i] + ".html")

        easygui.codebox(text=result_url.strip(),
                        title="Create Html Url", msg="Copy the url")

    elif choise_action == "Open Html & Upload to FTP":
        for i in range(len(path_list)):
            cmd = "start " + path_list[i][:path_list[i].index('/') + 1] + "\"" + \
                path_list[i][path_list[i].index('/') + 1:] + ".html\""
            system("start cmd /c \"" + cmd + "\"")
            ftp_upload(path_list[i], webtitle_list[i], file_array_list[i])
            result_url += "{}\nhttp://{}/~{}/{}.html\n\n".format(
                webtitle_list[i], host, user, urllib.parse.quote(webtitle_list[i]))
            result_url += "FTP user {} used {} MB".format(
                user, str(int(ftp_used_size / 1024 / 1024)))
        easygui.codebox(text=result_url.strip(),
                        title="Create Html Url", msg="Copy the url")

    elif choise_action == "Exit":
        pass

    else:
        pass


if __name__ == "__main__":
    main()
