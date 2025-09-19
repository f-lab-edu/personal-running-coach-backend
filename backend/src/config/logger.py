import logging
import sys


# logging.basicConfig(
#     level=logging.WARNING,
#     format="%(asctime)s [%(levelname)s][%(filename)s].%(funcName)s: %(message)s",
#     datefmt="%H:%M:%S",
#     handlers=[
#         # logging.StreamHandler(sys.stdout),
#         logging.FileHandler("server.log", encoding='utf-8')
#     ],
# )


# def get_logger(name:str) -> logging.Logger:
#     return logging.getLogger(name)


def get_logger(name: str = "app", filename: str = "server.log") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.WARNING)  # WARNING 이상만
    
    if not logger.handlers:  # 중복 방지
        fh = logging.FileHandler(filename, encoding="utf-8")
        fh.setLevel(logging.WARNING)
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s][%(filename)s].%(funcName)s: %(message)s",
            datefmt="%H:%M:%S"
        )
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    
    # root 로거로 전달 안 함 → sqlalchemy 등 다른 라이브러리 로그 차단
    logger.propagate = False

    return logger