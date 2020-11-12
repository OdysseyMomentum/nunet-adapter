import os

"""
Get container name for docker purposes
"""
try:
    CONTAINER_NAME = os.environ['NUNET_CONTAINER_NAME']
except:
    CONTAINER_NAME = "nunet"    # default container name


if CONTAINER_NAME == "production_nunet":
    try:
        MAX_LOAD = int(os.environ['MAX_LOAD_PRODUCTION'])
    except:
        MAX_LOAD = 60        
elif CONTAINER_NAME == "test_nunet":
    try:
        MAX_LOAD = int(os.environ['MAX_LOAD_SYSTEM_TEST'])
    except:
        MAX_LOAD = 60
elif CONTAINER_NAME == "local_nunet_no_persist":
    try:
        MAX_LOAD = int(os.environ['MAX_LOAD_LOCAL'])
    except:
        MAX_LOAD = 60
else:
    MAX_LOAD = 60

