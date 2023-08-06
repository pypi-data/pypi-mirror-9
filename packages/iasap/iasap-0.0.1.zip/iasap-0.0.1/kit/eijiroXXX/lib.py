import os, sys

def sys_path_append_parent_dir(file_path, n_up):
    if os.path.islink(file_path):
        file_path = os.path.realpath(file_path)
    here = os.path.abspath(file_path)
    ups = ""
    if n_up:
        ups = os.path.join(*([".."] * n_up))
    parent_dir = os.path.join(os.path.dirname(here), ups)
  # print("parent_dir =", parent_dir)
    sys.path.append(parent_dir)
