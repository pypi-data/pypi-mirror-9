from __future__ import absolute_import

from ..properties import Int, String, Float, Auto, Instance, Tuple, Either, Include
from ..mixins import LineProps

from .renderers import GuideRenderer
from .tickers import Ticker

class Grid(GuideRenderer):
    """ 1D Grid component """
    dimension = Int(0)
    bounds = Either(Auto, Tuple(Float, Float))

    x_range_name = String('default')
    y_range_name = String('default')

    ticker = Instance(Ticker)

    grid_props = Include(LineProps)
