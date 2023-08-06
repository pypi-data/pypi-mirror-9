
import os

import fantail

PARAMCACHE = {}

def get_recursive_param(here, filename):
    """
    Recursively load yaml files starting from the directory 'here'
    """

    conf = []

    while True:
        if os.path.isdir(here):
            here_c = os.path.join(here, filename)
            if os.path.exists(here_c):
                conf.append(here_c)

        parent = os.path.dirname(here)

        if parent == '/':  # no config in the root - that would be evil!
            break
            
        here = parent

    rv = fantail.Fantail()
    
    for c in conf[::-1]:
        fullname = os.path.expanduser(os.path.abspath(c))
        if fullname in PARAMCACHE:
            y = PARAMCACHE[fullname]
        else:
            y = fantail.yaml_file_loader(fullname)
            PARAMCACHE[fullname] = y
        rv.update(y)
    return rv
