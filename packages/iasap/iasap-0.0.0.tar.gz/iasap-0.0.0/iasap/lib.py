import sys, os
import datetime, argparse

import logging as _logger
import configparser

global logger
logger = _logger

CHARACTORS_PRINTED_PER_LINE = 79
CPPL = CHARACTORS_PRINTED_PER_LINE

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

def start_logger(script_name, log_dir=os.path.curdir, log_level=logger.INFO):
    # 通常使用時は、log_dir=os.path.curdir を想定している。
    # log_dir が空文字であれば、log の出力先を sys.stderr に変更する。

    basename = os.path.basename(script_name)
    if log_dir:
        log_base = ".".join((basename, "log"))
        log_path = os.path.join(log_dir, log_base)

        # http://docs.python.jp/3.4/library/logging.html#logging.basicConfig
        # stream: 指定されたストリームを StreamHandler の初期化に使います。
        # この引数は 'filename' と同時には使えないことに注意してください。
        # 両方が指定されたときには ValueError が送出されます。
        # logger.basicConfig(filename='/dev/null', level=logger.INFO)
        # logger.basicConfig(stream=sys.stderr, level=logger.DEBUG)
        logger.basicConfig(filename=log_path, level=log_level)
    else:
        logger.basicConfig(stream=sys.stderr, level=log_level)

    log_prefix = "INFO:root:"
    horizontal = "=" * (CPPL - len(log_prefix))
    _now = datetime.datetime.now()
    body = "{} start! at {} ".format(basename, _now)
    value = "=" * (CPPL - (len(log_prefix) + len(body)))

    logger.info(horizontal)
    logger.info(body + value)
    logger.info(horizontal)

def _merge_kv(first, second, third={}):
    kv = {}
    for k, v in first.items():
        kv[k] = v
    for k, v in second.items():
        kv[k] = v
    for k, v in third.items():
        kv[k] = v
    logger.debug("kv in _merge_kv() =")
    logger.debug(kv)
    logger.debug("\n")
    return kv

def _get_kv_by_conf(path, section):
    logger.debug("path =")
    logger.debug(path)
    with open(path) as f:
        config = configparser.ConfigParser()
        config.read_file(f, section)
    kv = {}
    for key, value in config[section].items():
        if value:
            kv[key] = value
    if kv["limit"]:
        kv["limit"] = int(kv["limit"])
    logger.debug("kv in _get_kv_by_conf() =")
    logger.debug(kv)
    logger.debug("\n")
    return kv

def _set_kv_by_defaults(defaults=None):
    logger.debug("kv in _set_kv_by_defaults() =")
    logger.debug(defaults)
    logger.debug("\n")
    return defaults

def merge_kv_by_defaults_and_argument(defaults=None):
    kv_defaults = _set_kv_by_defaults(defaults)
    kv_argment = _get_kv_by_argument(defaults)
    kv_tmp = _merge_kv(kv_defaults, kv_argment)
    return kv_tmp, kv_defaults, kv_argment

def set_kv_for_regular(kv_defaults, kv_argment, conf_path, section):
    kv_conf = _get_kv_by_conf(conf_path, section)
    kv = _merge_kv(kv_defaults, kv_conf, kv_argment)
    return kv

def _get_kv_by_argument(defaults=None):
    parser = argparse.ArgumentParser(description='argment.')

    parser.add_argument('--conf', metavar='f', dest='conf',
                       default=defaults["conf"],
                       help='default conf path is {}.'.format(defaults["conf"]))
    parser.add_argument('--dbpath', metavar='f', dest='dbpath',
                       default=defaults["dbpath"],
                       help='default sqlite dbpath is {}'.format(defaults["dbpath"]))
    parser.add_argument('--mode', metavar='s', dest='mode',
                       default=defaults["mode"],
                       help='default iasap library mode is tkinter, curses or one-shot.')
    parser.add_argument("--limit", metavar="N", dest="limit",
                         type=int, default=defaults["limit"],
                         help="max number of rows as select result, default is {}".format(defaults["limit"]))
    parser.add_argument("--debug", help="debug mode switch, default is False.", action="store_true")
    parser.add_argument('args', nargs=argparse.REMAINDER)

    args = parser.parse_args()
    kv = {}
    logger.debug("sys.argv =")
    logger.debug(sys.argv)
    logger.debug("args =")
    logger.debug(args)
    logger.debug("vars(args) =")
    logger.debug(vars(args))
#   logger.debug("args.items() =")
#   logger.debug(args.items())
    shell_command = "`".join(sys.argv)
    for k, v in vars(args).items():
        logger.debug("k={}, v={}".format(k, v))
        if "--{}".format(k) in shell_command:
            # user $B;XDj(B
            kv[k] = v
    kv["args"] = args.args
    logger.debug("kv in _get_kv_by_argument() =")
    logger.debug(kv)
    logger.debug("\n")
    return kv

