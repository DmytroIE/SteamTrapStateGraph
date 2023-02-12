from cycler import cycler
from enum import Enum


class CsvFileSources(str, Enum):
    SteamIQ = 'SteamIQ'
    iLoop = 'iLoop'

class ResampOperations(str, Enum):
    NoResample = 'No resample'
    Mean = 'Mean'

class LeakUnits(str, Enum):
    Percent = 'Percent'
    Mass = 'Mass'
    Energy = 'Energy'


#print(ResampOperations)
#print(dir(ResampOperations))
#print(list(ResampOperations))
#print(ResampOperations.__members__.keys())

class LineColors(str, Enum):
    Orange = 'tab:orange'
    Cyan = 'tab:cyan'

    # @classmethod
    # def keys(cls):
    #     return cls.__members__.keys()

line_colors_map = {
    'Orange': 'tab:orange',
    'Cyan': 'tab:cyan',
    'Green': 'tab:green',
}

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