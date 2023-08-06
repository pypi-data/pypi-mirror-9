#!/usr/bin/env python

import socket

colors = ['white', 'red', 'orange', 'yellow', 'green', 'cyan', 'blue',
          'purple', 'black', 'question', 'exclamation']


class AnyBar():
    def __init__(self, port=1738, address='localhost'):
        self.port = port
        self.address = address
        self.socket = socket.socket(socket.AF_INET,
                                    socket.SOCK_DGRAM)

    def change(self, color):
        if color not in colors:
            raise ValueError('Color is not valid. It must be one of the '
                             'following: {}'.format(', '.join(colors)))

        self.socket.sendto(color, (self.address, self.port))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Change color of AnyBar')
    parser.add_argument('color', choices=colors,
                        help='The color you want to change to.')
    parser.add_argument('port', type=int, nargs='?', default=1738,
                        help='The port of the AnyBar instance '
                             '(default: 1738).')
    parser.add_argument('address', nargs='?', default='localhost',
                        help='The address of the AnyBar instance '
                             '(default: localhost).')
    args = parser.parse_args()

    AnyBar(port=args.port).change(args.color)
