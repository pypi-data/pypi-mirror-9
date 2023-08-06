# -*- coding: utf-8 -*-

from __future__ import print_function
import subprocess
import sys
import os
import argparse

def usage():
    print("genee-puppet init")
    print("genee-puppet run [-n name] [-p port]")
    print("    default: name=puppetmaster, port=8140")

def puppet_init(args):
    if not os.path.exists("ssl.d"):
        os.mkdir("ssl.d")
    if not os.path.exists("conf.d"):
        subprocess.check_call("git clone https://bitbucket.org/genee/genee-puppet.git conf.d", shell=True)

def puppet_run(args):

    name = args.name
    port = args.port

    if not os.path.exists('conf.d') or not os.path.exists('ssl.d'):
        print('Run "genee-puppet init" first.')
        sys.exit(0)

    try:
        cmd = ("docker run --name %s -d --restart=always -v %s:/opt/puppet -v %s:/var/lib/puppet/ssl -v /dev/log:/dev/log -p %d:8140 genee/puppetmaster" % (name, os.getcwd() + '/conf.d', os.getcwd() + '/ssl.d', port))
        print(cmd + "\n")
        print(subprocess.check_output(cmd, shell=True, universal_newlines=True))
    except subprocess.CalledProcessError as e:
        return

def main():

    argparser = argparse.ArgumentParser(prog='genee-puppet')

    argparser.add_argument('-C', '--path', type=str, default=os.getcwd())

    subparsers = argparser.add_subparsers(dest='subcommand')

    init_parser = subparsers.add_parser('init')

    run_parser = subparsers.add_parser('run')
    run_parser.add_argument('-n', '--name', type=str, default='puppetmaster')
    run_parser.add_argument('-p', '--port', type=int, default=8140)

    help_parser = subparsers.add_parser('help')

    args = argparser.parse_args()

    if args.subcommand is None:
        usage()
        sys.exit(1)

    cwd = args.path
    if cwd and cwd != os.getcwd():
        if not os.path.exists(cwd):
            os.makedirs(cwd)
        os.chdir(cwd)

    if args.subcommand == 'init':
        puppet_init(args)
    elif args.subcommand == 'run':
        puppet_run(args)
    else:
        usage()
        sys.exit(1)

if __name__ == "__main__":
    main()
