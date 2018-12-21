import os


def main():
    cmd = ""
    with open(os.path.abspath("./list/url_list"), "r", encoding='utf8', newline=None) as f:
        for line in f:
            if line.strip() == "":
                continue
            if cmd == "":
                cmd = 'start "" "{}"'.format(line)
            else:
                cmd += ' & start "" "{}"'.format(line)
    print(cmd)
    os.system("start cmd /c \"{}\"".format(cmd.replace("\n", "")))


if __name__ == "__main__":
    main()
