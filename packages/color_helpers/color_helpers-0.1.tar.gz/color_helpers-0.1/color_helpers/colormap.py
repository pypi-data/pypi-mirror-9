import pandas as pd
import numpy as np

from . import get_data_directory


class ColorMap(object):
    def __init__(self, colors_frame):
        self.colors_frame = colors_frame

    @classmethod
    def from_csv(cls, color_map_csv_path):
        colors_frame = pd.DataFrame.from_csv(color_map_csv_path,
                                             index_col=False)
        return cls(colors_frame.set_index(['color', 'group']))

    @property
    def colors(self):
        return self.colors_frame.index.get_level_values(0).unique()

    @property
    def shades(self):
        return self.colors_frame.index.get_level_values(1).unique()

    def get_hex_color(self, color, shade):
        return '#%02x%02x%02x' % tuple([self.colors_frame.loc[(color, shade)]
                                        [c] for c in 'rgb'])


class ShowMeTheNumbersMap(ColorMap):
    def __init__(self):
        color_map = ColorMap.from_csv(get_data_directory()
                                      .joinpath('show_me_the_numbers-'
                                                'colour_palette.csv'))
        super(ShowMeTheNumbersMap, self).__init__(color_map.colors_frame)

    @property
    def colors(self):
        colors = self.colors_frame.index.get_level_values(0).unique()
        return np.roll(colors, -1)
