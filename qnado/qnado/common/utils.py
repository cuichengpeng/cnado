import os
import traceback


def get_dir_path(path, *paths):
    dir_path = os.path.join(path, *paths)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path


def get_trace_info(exc):
    frame_list = []
    tbe = traceback.TracebackException.from_exception(exc)
    for line in tbe.format():
        frame_list.append(line)
    return ''.join(frame_list)
