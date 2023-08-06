#! /usr/bin/env python
import argparse
import browler


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help='path/to/config.json')
    args = parser.parse_args()
    filename = args.config