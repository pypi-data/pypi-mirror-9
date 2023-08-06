import time
import sys
import os

import logging

DEBUG = True
LOG2CONSOLE = True
LOG2FILE = False

# get logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# log to console
if LOG2CONSOLE:
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(fmt='%(levelname)s: \t %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
    
    if DEBUG:
        console_level = logging.DEBUG
    else:
        console_level = logging.INFO
    
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(console_level)
    
    logger.addHandler(console_handler)

# log to file
if LOG2FILE:
    try:
        fname = sys.argv[0].split('.')[0]+"_"+time.strftime('%y%m%d-%H%M%S')+".log"
        
        file_handler = logging.FileHandler(filename=fname, mode='a')
        file_formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s: \t %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
        file_level = logging.DEBUG
    
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(file_level)
    
        logger.addHandler(file_handler)
    except Exception as err:
        logging.error('Could not create log file!')
        logging.error('Got message: {}'.format(err))


class Timer():
    '''
    Provides a context manager that takes the time of a code block.
    
    Parameters
    ----------
    
    label : str
        The 'name' of the code block which is timed
    
    verb : int
        Level of verbosity
    '''
    def __init__(self, label="~", verb=4):
        self.label = label
        self.verb = verb

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, *args):
        self.delta = time.time() - self.start
        logging.debug("---> [%s elapsed %f s]"%(self.label, self.delta))