import os


def main():
    cmd = ""
    with open("./list/url_list", "r", encoding='utf8') as f:
        for line in f:
            if line.strip() == "":
                continue
            if cmd == "":
                cmd = 'start "" "{}"'.format(line.strip())
            else:
                cmd += ' & start "" "{}"'.format(line.strip())
    print(cmd)
    os.system("start cmd /c \"{}\"".format(cmd))


if __name__ == "__main__":
    main()
