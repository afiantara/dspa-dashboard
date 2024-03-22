import logging
LOGFILE='./tks.log'

def loginit():
    LOG_FILENAME = LOGFILE
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)   
    logging.info('init logging...')

def info(message):
    logging.info(message)

def debug(message):
    logging.debug(message)

def error(message):
    logging.error(message)    