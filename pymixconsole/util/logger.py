import sys
import logging

LOG_NAME = "pymixconsole"

def getLog(name):                                                                                        
    return logging.getLogger(name);                                                                                                                                                              
                                                                  
def createLog(name):

    root = logging.getLogger(name)
    root.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)

    return root