import logging


class GetLogger:
    user = ""
    filename = ""

    def __init__(self, user, filename):
        self.user = user
        self.filename = filename
        pass

    def initial_logger(self):
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)-21s %(name)-6s %(levelname)-10s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            handlers=[logging.FileHandler('./logs/{}.log'.format(self.filename), 'w', 'utf-8'), ])

        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(name)s: %(levelname)-10s %(message)s')
        console.setFormatter(formatter)
        logging.getLogger(self.user).addHandler(console)
        return logging.getLogger(self.user)
