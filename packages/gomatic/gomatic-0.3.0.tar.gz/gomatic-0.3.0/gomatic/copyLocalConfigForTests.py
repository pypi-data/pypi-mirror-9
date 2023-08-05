#!/usr/bin/env python

from gomatic import *


if __name__ == '__main__':
    server = GoCdConfigurator(HostRestClient("localhost:8153"))

    open('test-data/config-with-source-exclusions.xml', 'w').write(server.current_config())
