# Copyright 2015 Laszlo Attila Toth
# Distributed under the terms of the GNU General Public License v3


import sys
from dewi.core.application import MainApplication
from dewi.loader.loader import PluginLoader


def main():
    loader = PluginLoader()
    app = MainApplication(loader, 'dewi')
    app.run(sys.argv[1:])

if __name__ == '__main__':
    main()
