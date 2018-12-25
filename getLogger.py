import logging


class GetLogger:
    def __init__(self):
        pass

    def initial_logger(self, user, filename):
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)-21s %(name)-6s %(levelname)-10s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            handlers=[logging.FileHandler('./logs/{}.log'.format(filename), 'w', 'utf-8'), ])

        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(name)s: %(levelname)-10s %(message)s')
        console.setFormatter(formatter)
        logging.getLogger(user).addHandler(console)
        return logging.getLogger(user)
