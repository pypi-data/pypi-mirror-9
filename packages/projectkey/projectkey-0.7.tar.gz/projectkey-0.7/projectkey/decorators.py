

def ignore_ctrlc(method):
    method.ignore_ctrl_c = True
    return method