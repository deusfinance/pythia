import argparse
import sys


def read(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description="The parsing commands lists.")
    parser.add_argument("-k", "--pkey", help="Set node private key.")
    parser.add_argument("-d", "--node", help="Run specific node. Config file .env.<node> should be exist.")
    opts = parser.parse_args(args)
    return opts
