import argparse, os, re, shutil

PATTERN = "XXX"

def sed(path, pattern, repl):
    print("sed(path={}, pattern={}, repl={})".format(path, pattern, repl))
    f = open(path, "r")
    tmp_path = path + ".tmp"
    t = open(tmp_path, "w")
    for old_line in f:
        new_line = re.sub(pattern, repl, old_line)
        t.write(new_line)
    t.close()
    f.close()
    os.remove(path)
    os.rename(tmp_path, path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="init eijiro root directory.")

    parser.add_argument("--xxx", metavar="n", dest="ver",
                       required=True,
                       help=("お使いの英辞郎辞書データの"
                             " Version を指定します。"
                             "「英辞郎辞書データVer98.」をお使いなら、"
                             "--xxx=98 とします。"))
    args = parser.parse_args()

    ver = args.ver
    eijiroXXX = "eijiro" + ver
    eijiroXXX_root = os.path.join("..", eijiroXXX)
    print("eijiroXXX_root =", eijiroXXX_root)

    try:
        shutil.rmtree(eijiroXXX_root)
    except FileNotFoundError as e:
      # print("e =", e)
      # print("e.args =", e.args)
        if e.args == (2, 'No such file or directory'):
            pass
        else:
            raise FileNotFoundError(*e.args)
    os.mkdir(eijiroXXX_root)

    for old_basename in os.listdir("."):
        if old_basename == "init_eijiroXXX.py":
            continue
        if old_basename.endswith("swp"):
            # 糞 Vim !
            continue
        new_basename = re.sub(PATTERN, ver, old_basename)

        old_path = os.path.join(".", old_basename)
        new_path = os.path.join(eijiroXXX_root, new_basename)

        cmd = "shutil.copy({}, {})".format(old_path, new_path)
        shutil.copy(old_path, new_path)
        print(cmd)
        sed(new_path, PATTERN, ver)
        sed(new_path, "OS_SYS_EXECUTE", os.sys.executable)
