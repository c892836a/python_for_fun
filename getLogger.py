import logging


class GetLogger:
    user = ""
    filename = ""

    def __init__(self, user, filename):
        self.user = user
        self.filename = filename

    def initial_logger(self):
        result_logger = logging.getLogger(self.user)
        file_handler = logging.FileHandler(
            './logs/{}.log'.format(self.filename), mode='w', encoding='utf-8')
        file_formatter = logging.Formatter(
            '%(asctime)-21s %(name)-8s %(levelname)-10s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        result_logger.setLevel(logging.INFO)
        file_handler.setFormatter(file_formatter)
        result_logger.addHandler(file_handler)
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(name)-8s: %(levelname)-10s %(message)s')
        console.setFormatter(formatter)
        result_logger.addHandler(console)

        return result_logger
