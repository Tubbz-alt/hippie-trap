#!/usr/bin/python
import abc
import math
import colorsys
import generator
import random
from color import Color, hueToColor
import common

class ColorSource(common.ChainLink):

    def __init__(self, gen, gen2 = None, gen3 = None):
        super(ColorSource, self).__init__()
        self.g = gen
        self.g2 = gen2
        self.g3 = gen3
        self.next = None

    @abc.abstractmethod
    def __getitem__(self, t):
        pass

class ConstantColor(ColorSource):

    def __init__(self, color):
        self.color = color
        super(ConstantColor, self).__init__(None)

    def describe(self):
        desc = common.make_function(common.FUNC_CONSTANT_COLOR, (common.ARG_COLOR,))
        desc += common.pack_color(self.color)
        print "%s()" % (self.__class__.__name__)
        return desc + self.describe_next()

    def __getitem__(self, t):
        return self.call_next(t, self.color)

class RandomColorSequence(ColorSource):
    '''
       Return colors that appear _random_ to a human.
    '''

    def __init__(self, period, seed=0):
        self.period = period
        self.seed = seed
        super(RandomColorSequence, self).__init__(None)

    def describe(self):
        desc = common.make_function(common.FUNC_RAND_COL_SEQ, (common.ARG_VALUE,common.ARG_VALUE))
        desc += common.pack_fixed(self.period)
        desc += common.pack_fixed(self.seed)
        print "%s(%.3f, %.3f)" % (self.__class__.__name__, self.period, self.seed)
        return desc + self.describe_next()

    def __getitem__(self, t):
        random.seed(self.seed + (int)(t / self.period))
        return self.call_next(t, hueToColor(random.random()))

class HSV(ColorSource):

    def __init__(self, gen, gen2 = None, gen3 = None):
        super(HSV, self).__init__(g, gen2, gen3)

    def describe(self):
        desc = common.make_function(common.FUNC_COLOR_WHEEL, (common.ARG_VALUE,common.ARG_VALUE,common.ARG_FUNC))
        desc += common.pack_fixed(self.period)
        desc += common.pack_fixed(self.seed)
        print "%s(" % (self.__class__.__name__),
        if self.g:
            desc += self.g.describe()
        print ")"
        return desc + self.describe_next()

    def __getitem__(self, t):
        if self.gen2 and self.gen3:
            col = colorsys.hsv_to_rgb(self.g[t], self.gen2[t], self.gen3[t])
        elif self.gen2:
            col = colorsys.hsv_to_rgb(self.g[t], self.gen2[t], 1)
        else:
            col = colorsys.hsv_to_rgb(self.g[t], 1, 1)
        return self.call_next(t, Color(int(col[0] * 255), int(col[1] * 255), int(col[2] * 255)))

class Rainbow(ColorSource):

    def __init__(self, gen):
        super(Rainbow, self).__init__(gen)

    def describe(self):
        desc = common.make_function(common.FUNC_RAINBOW, (common.ARG_FUNC,))
        print "%s(" % (self.__class__.__name__),
        if self.g:
            desc += self.g.describe()
        print ")"
        return desc + self.describe_next()

    def __getitem__(self, t):
        color = [0,0,0]

        wheel_pos = 255 - int(255 * self.g[t])
        if wheel_pos < 85:
            color[0] = int(255 - wheel_pos * 3)
            color[1] = 0
            color[2] = int(wheel_pos * 3)
        elif wheel_pos < 170:
            wheel_pos -= 85
            color[0] = 0
            color[1] = int(wheel_pos * 3)
            color[2] = 255 - int(wheel_pos * 3)
        else:
            wheel_pos -= 170
            color[0] = int(wheel_pos * 3)
            color[1] = 255 - int(wheel_pos * 3)
            color[2] = 0

        return self.call_next(t, Color(color[0], color[1], color[2]))