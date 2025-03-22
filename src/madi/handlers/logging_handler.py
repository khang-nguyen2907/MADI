import logging
import sys

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()]
)

# def get_logger(name: str):
#     logger = logging.getLogger(name)
#     logger.setLevel(logging.INFO)
#     return logger

# def log_info(logger, message, args): 
#     logger.info(
#         f"{"*"*25}{message}{"*"*25}\n"
#     )
#     logger.info(args)
#     logger.info(
#         f"{"*"*25}{"*"*len(message)}{"*"*25}\n"
#     )

class Log: 
    def __init__(self, name): 
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
    
    def info(self, message, args=""): 
        self.logger.info(
            f"{"*"*25}{message}{"*"*25}\n"
        )
        self.logger.info(args)
        self.logger.info(
            f"{"*"*25}{"*"*len(message)}{"*"*25}\n"
        )
    def error(self, message, args=""): 
        self.logger.error(
            f"{"*"*25}{message}{"*"*25}\n"
        )
        self.logger.error(args)
        self.logger.error(
            f"{"*"*25}{"*"*len(message)}{"*"*25}\n"
        )
    def title(self, title): 
        self.logger.info(
            f"{"*"*25}{"*"*len(title)}{"*"*25}\n"
        )

if __name__ == "__main__": 
    log_obj = Log(__name__)
    log_obj.info("Message", 1+1)
