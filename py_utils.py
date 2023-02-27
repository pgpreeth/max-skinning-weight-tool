import sys

def check_if_python_3():
    if sys.version_info.major == 3:
        return True
    return False


def reload_module(module):
    if not check_if_python_3():
        from imp import reload
        reload(module)
        return
    else:
        from importlib import reload
        reload(module)
        return