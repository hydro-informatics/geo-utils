import os, sys

sys.path.append(r'' + os.path.abspath(''))
sys.path.insert(0, r'' + os.path.abspath('') + '/geo_utils')

try:
    logging.getLogger()
except:
    pass
