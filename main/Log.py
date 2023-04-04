import logging

def create_logger(logger_name):
    logger = logging.getLogger(logger_name)

    # 로그의 출력 기준 설정
    logger.setLevel(logging.INFO)

    # log 출력 형식
    formatter = logging.Formatter('%(asctime)s - %(message)s')

    # log 출력
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # log를 파일에 출력
    file_handler = logging.FileHandler(f'./log/{logger_name}.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger