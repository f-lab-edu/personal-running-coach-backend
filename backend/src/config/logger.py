import logging
from pathlib import Path
import os

BASE = Path(__file__).resolve().parent.parent.parent
LOG_DIR = BASE / "logs"   # docker-compose volume과 연결한 경로
print(LOG_DIR)
os.makedirs(LOG_DIR, exist_ok=True)

def get_logger(name: str = "app", filename: str = "server.log") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.WARNING)  # WARNING 이상만
    
    if not logger.handlers:  # 중복 방지
        log_path = os.path.join(LOG_DIR, filename)
        fh = logging.FileHandler(log_path, encoding="utf-8")
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

## stdout 으로 로그 출력
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