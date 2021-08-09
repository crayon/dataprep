'''Plotly colors

This script sets consistent colors for plotly plots.

ToDo:
    :: Test thoroughly

Usage:
    :: Just import in the beginning of your script/nb
    :: This is only meant for 1-3 color plots as for now

'''

from plotly import io as pio
from plotly import graph_objects as go
from plotly import express as px

# creating crayon template
pio.templates["crayon"] = go.layout.Template(
    layout_colorway=['#094E5D', '#FF6A4C', '#04242D', '#ff370f', '#FF9449'])
pio.templates["crayon"]["layout"]["plot_bgcolor"] = 'rgba(0,0,0,0)'
pio.templates["crayon"]["layout"]["paper_bgcolor"] = 'rgba(0,0,0,0)'
pio.templates["crayon"]["layout"]["yaxis"]["gridcolor"] = '#000000'

# setting template as default, adding crayon colors atop standard plotly
pio.templates.default = pio.templates["plotly+crayon"]

# set plotly express colors
px.defaults.color_discrete_sequence = ['#094E5D', '#FF6A4C', '#04242D', '#ff370f', '#FF9449']
