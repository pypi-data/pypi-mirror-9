################################################################
# haufe.sharepoint
################################################################

import os
import sys
import logging

handler = logging.StreamHandler(sys.stdout) 
frm = logging.Formatter("%(asctime)s %(levelname)s: %(message)s", 
                              "%d.%m.%Y %H:%M:%S") 
handler.setFormatter(frm)
logger = logging.getLogger() 
logger.addHandler(handler) 
logger.setLevel(logging.INFO)
if 'DEBUG_SUDS' in os.environ:
    logger.setLevel(logging.DEBUG)