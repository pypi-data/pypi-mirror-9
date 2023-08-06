# Copyright 2015 Laszlo Attila Toth
# Distributed under the terms of the GNU General Public License v3

import argparse


class Command:
    name = ''
    aliases = list()
    description = ''

    def register_arguments(self, parser: argparse.ArgumentParser) -> None:
        pass

    def run(self, args: argparse.Namespace):
        raise NotImplementedError
