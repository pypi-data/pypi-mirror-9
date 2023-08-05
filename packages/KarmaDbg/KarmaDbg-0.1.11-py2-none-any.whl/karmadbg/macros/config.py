import shutil
import os.path
import argparse

def home(*args):
    homedir = os.path.expanduser("~")
    return os.path.join(homedir, ".karmadbg") 

def config(vars):

    def config_clear():
        try:
            shutil.rmtree(home())
            return "Config is cleared"
        except:
            return "Config does not exist"

    def config_create():
        pass

    def config_extpath_add(path):
        print "add extension path: ", path

    def config_extpath_reset():
        pass

    parser = argparse.ArgumentParser(prog='%config')
    
    subparsers = parser.add_subparsers(dest='command')
    parserClear= subparsers.add_parser('clear', help='clear config')
    parserExt = subparsers.add_parser('extpath', help='extension path')
    group = parserExt.add_mutually_exclusive_group(required=True)
    group.add_argument('--add', help='add extension path')
    group.add_argument('--reset', help='remove extension paths', action='store_true')

    try:

        args = parser.parse_args(vars)
        if args.command=='clear':
            return config_clear()

        if args.command=='extpath':
            if args.reset:
                return config_extpath_reset()
            return config_extpath_add(args.add)

    except SystemExit:
        return

