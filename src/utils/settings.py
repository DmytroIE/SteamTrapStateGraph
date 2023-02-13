from cycler import cycler
from enum import Enum
import itertools

class CsvFileSources(str, Enum):
    SteamIQ = 'SteamIQ'
    iLoop = 'iLoop'

class ResampleOperations(str, Enum):
    NoResample = 'No resample'
    Mean = 'Mean'

class LeakUnits(str, Enum):
    Percent = 'Percent'
    Mass = 'Mass'
    Energy = 'Energy'

leak_units_symbol_map = {
    LeakUnits.Percent: '%',
    LeakUnits.Mass: 'kg/h',
    LeakUnits.Energy: 'kWh'
}

#print(ResampOperations)
#print(dir(ResampOperations))
#print(list(ResampOperations))
#print(ResampOperations.__members__.keys())

class LineColors(str, Enum):
    Orange = 'Orange'
    Cyan = 'Cyan'
    Green = 'Green'


class AuxLineColors(str, Enum):
    DeepSkyBlue = 'DeepSkyBlue'
    Red = 'Red'
    Lime = 'Lime'
    Magenta = 'Magenta'
    Gold = 'Gold'

    # @classmethod
    # def keys(cls):
    #     return cls.__members__.keys()

# line_colors_map = {
#     'Orange': 'tab:orange',
#     'Cyan': 'tab:cyan',
#     'Green': 'tab:green',
# }

line_colors_map = {
    LineColors.Orange: 'tab:orange',
    LineColors.Cyan: 'tab:cyan',
    LineColors.Green: 'tab:green'
}

aux_line_colors_map = {
    AuxLineColors.DeepSkyBlue: 'deepskyblue',
    AuxLineColors.Red: 'tab:red',
    AuxLineColors.Lime: 'lime',
    AuxLineColors.Magenta: 'm',
    AuxLineColors.Gold: 'gold'
}

aux_line_cycler = itertools.cycle(aux_line_colors_map.values())

PlotStyleSettings = {
'axes.edgecolor': 'grey',
'axes.facecolor': 'black',
'axes.labelcolor': 'white',
'axes.grid': 'True',
'axes.prop_cycle': cycler('color', line_colors_map.values()),
'boxplot.boxprops.color': 'white',
'boxplot.capprops.color': 'white',
'boxplot.flierprops.color': 'white',
'boxplot.flierprops.markeredgecolor': 'white',
'boxplot.whiskerprops.color': 'white',
'figure.edgecolor': 'black',
'figure.facecolor': 'black',
'grid.color': 'grey',
'grid.alpha': 0.5,
'grid.linewidth': 0.8,
'lines.color': 'C0', # has no affect on plot(); see axes.prop_cycle
'lines.linestyle': '-',
'lines.linewidth': 2.0,
'patch.edgecolor': 'white',
'savefig.dpi': 150,
'savefig.edgecolor': 'black',
'savefig.facecolor': 'black',
'text.color': 'white',
'xtick.color': 'white',
'ytick.color': 'white'
}

YAxisLimits = [0, 50]