# -*- coding: utf-8 -*-

"""
Usage: pybox <width> <height>
"""


class Unicode(object):
    h = u'\u2500'
    v = u'\u2502'
    tl = u'\u250C'
    tr = u'\u2510'
    bl = u'\u2514'
    br = u'\u2518'


class Box(object):
    def __init__(self, style):
        self.style = style

    @property
    def h(self):
        return self.style.h

    @property
    def v(self):
        return self.style.v

    @property
    def tl(self):
        return self.style.tl

    @property
    def tr(self):
        return self.style.tr

    @property
    def bl(self):
        return self.style.bl

    @property
    def br(self):
        return self.style.br

    def draw_box(self, width, height):
        print self.tl + (self.h * (width - 2)) + self.tr
        for _ in xrange(height - 2):
            print self.v + (' ' * (width - 2)) + self.v
        print self.bl + (self.h * (width - 2)) + self.br


def main():
    from docopt import docopt

    arguments = docopt(__doc__, version='pybox 0.1')
    b = Box(Unicode())
    b.draw_box(int(arguments['<width>']), int(arguments['<height>']))

if __name__ == '__main__':

    main()



