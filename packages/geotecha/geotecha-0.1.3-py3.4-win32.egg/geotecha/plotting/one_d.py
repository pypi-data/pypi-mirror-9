# geotecha - A software suite for geotechncial engineering
# Copyright (C) 2013  Rohan T. Walker (rtrwalker@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/gpl.html.

"""Routines to produce some matplotlib plots for one dimesional data.

One dimensional data is basically x-y data. (i.e. no contour plot needed)

"""

from __future__ import division, print_function

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import brewer2mpl
import random
import itertools
import geotecha.mathematics.transformations as transformations
from geotecha.piecewise.piecewise_linear_1d import PolyLine
import geotecha.piecewise.piecewise_linear_1d as pwise
import warnings


def rgb_shade(rgb, factor=1, scaled=True):
    """Apply shade (darken) to a red, green, blue (rgb) triplet

    If rgba tuple is given the 'a' value is not altered.

    Parameters
    ----------
    rgb : tuple
        Triplet of rgb values.  Note can be an rgba value.
    factor : float
        Between 0 and 1. Factor by which to shade.  Default factor=1.
    scaled : bool
        If True then assumes RGB values aare scaled between 0, 1. If False
        rgb values are between 0 and 255.  Default scaled=True.

    Returns
    -------
    rgb_new : tuple
        New tuple of rgb (or rgba) values.

    See Also
    --------
    rgb_tint : Lighten an rgb triplet.

    Examples
    --------
    >>> x=rgb_shade((0.4, 0.8, 0.2), factor=0.5)
    >>> '{:.2f}, {:.2f}, {:.2f}'.format(*x)
    '0.20, 0.40, 0.10'

    """



    #calc from http://stackoverflow.com/a/6615053/2530083
    if factor<0 or factor>1:
        raise ValueError('factor must be between 0 and 1.  '
                         'You have {:g}'.format(factor))

    rgb_new = [v * factor for v in rgb[:3]]
    if len(rgb)==4:
        rgb_new.append(rgb[3])

    return tuple(rgb_new)


def rgb_tint(rgb, factor=0, scaled=True):
    """Apply tint (lighten) to a red, green, blue (rgb) triplet

    If rgba tuple is given the 'a' value is not altered.

    Parameters
    ----------
    rgb : tuple
        Triplet of rgb values.  Note can be an rgba value.
    factor : float
        Between 0 and 1. Factor by which to tint. Default factor=0.
    scaled : bool
        If True then assumes RGB values aare scaled between 0, 1. If False
        rgb values are between 0 and 255.  Default scaled=True.

    Returns
    -------
    rgb_new : tuple
        New tuple of rgb ( or rgba).

    See Also
    --------
    rgb_shade : Darken an rgb triplet.

    Examples
    --------
    >>> x=rgb_tint((0.4, 0.8, 0.2), factor=0.5)
    >>> '{:.2f}, {:.2f}, {:.2f}'.format(*x)
    '0.70, 0.90, 0.60'

    >>> x=rgb_tint((155, 205, 55), factor=0.5, scaled=False)
    >>> '{:.2f}, {:.2f}, {:.2f}'.format(*x)
    '205.00, 230.00, 155.00'

    """

    #calc from http://stackoverflow.com/a/6615053/2530083
    if factor<0 or factor>1:
        raise ValueError('factor must be between 0 and 1.  You have {:g}'.format(factor))

    if scaled:
        black=1.0
    else:
        black=255

    rgb_new = [v + (black-v) * factor for v in rgb[:3]]
    if len(rgb)==4:
        rgb_new.append(rgb[3])

    return tuple(rgb_new)



def copy_dict(source_dict, diffs):
    """Returns a copy of source_dict, updated with the new key-value
       pairs in diffs dict.


    Parameters
    ----------
    source_dict : dict
        Source dictionary.
    diffs : dict
        Dictionary with which to update `source_dict`.

    Returns
    -------
    out : dict
        Shallow copy of `source_dict` updated with `diffs` dict.

    References
    ----------
    http://stackoverflow.com/a/5551706/2530083

    Examples
    --------
    >>> d = copy_dict({'a':7, 'b':12}, {'c':13})
    >>> d['a']; d['b']; d['c']
    7
    12
    13

    >>> d = copy_dict({'a':7, 'b':12}, {'a':21, 'c':13})
    >>> d['a']; d['b']; d['c']
    21
    12
    13


    """
       #http://stackoverflow.com/a/5551706/2530083

    result=dict(source_dict) # Shallow copy, see addendum below
    result.update(diffs)
    return result


class MarkersDashesColors(object):
    """Nice looking markers, dashed lines, and colors for matplotlib line plots

    Use this object to create a list of style dictionaries.  Each style dict
    can be unpacked when passed to the matplotlib.plot command.  Each dict
    contains the appropriate keywords to set the marker, dashes, and color
    properties.  You can turn the list into a cycle using itertools.cycle
    To see the marker, dashes, and color options run the `demo_options' method.
    To choose a subset of styles see the `__call__` method.  To view what the
    chosen styles actually look like run the `construct_styles' and the
    `demo_styles` method

    Parameters
    ----------
    **kwargs : keyword arguments
        key value pairs to override the default_marker. e.g. color=(1.0,0,0)
        would change the default line and marker color to red. markersize=8
        would change all marker sizes to 8. Most likely value to change are
        color, markersize, alpha.  Defult values of the default_marker are:

        ================= ===========================================
        key               value
        ================= ===========================================
        markersize        5
        markeredgecolor   `almost_black`, '#262626'
        markeredgewidth   1
        markerfacecolor   `almost_black`, '#262626'
        alpha             0.9
        color             `almost_black`, '#262626'
        ================= ===========================================


    Attributes
    ----------
    almost_black : str
        hex string representing the default color, almost black '#262626'.
    color : matplotlib color
        Default color of markers and lines.  Default color=`almost_black`.
    dashes : list of tuples
        List of on, off tuples for use with matplotlib dashes.
        See `construct_dashes` method.
    colors : list of tuples
        List of rgb tuples describing colors.  See `construct_dashes`.
    markers : list of dict
        List of dict describing marker properties to pass to matplotlib.plot
        command.  See `construct_markers` method.
    default_marker : dict
        Default properties for markers.  These defaults will be overridden by
        the values in `markers`. Before initialization `default_marker` has
        the following keys.


    """

    almost_black = '#262626'
    def __init__(self, **kwargs):
        """Initialization of MarkersDashesColors object"""

        self.color = kwargs.get('color', self.almost_black)
        self.default_marker={#'marker':'o',
                             'markersize':5,
                             'markeredgecolor': self.color,
                             'markeredgewidth':1,
                             'markerfacecolor': self.color,
                             'alpha':0.9,
                             'color': self.color
                             }
        self.default_marker.update(kwargs)

        self.construct_dashes()
        self.construct_colors()

        self.construct_markers()
        self.merge_default_markers()
        self.styles=[]



    def __call__(self, markers=None,
                 dashes=None,
                 marker_colors=None,
                 line_colors=None):
        """List of styles to unpack in matplotlib.plot for pleasing lines/markers

        If `markers`, `dashes`, `marker_colors`, and `line_colors` are all
        ``None`` then styles will be a cycle through combos of markers, colors,
        and lines such that each default marker, line, color appears at least
        once.

        Parameters
        ----------
        markers : sequence
            List of ``int`` specifying  index of self.markers.
            Default markers=None, i.e. no markers.
        dashes : sequence
            List of ``int`` specifying index of self.dashes.
            Default dashes=None i.e. no line.
        marker_colors : sequence
            List of ``int`` specifying index of self.colors to apply to
            each marker. Default marker_colors=None i.e. use self.color
            for all markers.
        line_colors : sequence
            List of ``int`` specifying index of self.colors.
            Default line_colors=None i.e. use self.color for lines.


        """

        n = 0
        try:
            n=max([len(v) for v in [markers, dashes, marker_colors, line_colors] if v is not None])
        except ValueError:
            pass

        if n==0:
            markers = list(range(len(self.markers)))
            dashes = list(range(len(self.dashes)))
            marker_colors = list(range(len(self.colors)))
            line_colors = list(range(len(self.colors)))
            n = max([len(v) for v in [markers, dashes, marker_colors, line_colors] if v is not None])

        if markers is None: # no markers
            markers=itertools.cycle([None])
        else:
            markers=itertools.cycle(markers)
        if dashes is None: # no lines
            dashes=itertools.cycle([None])
        else:
            dashes=itertools.cycle(dashes)
        if marker_colors is None: #default color
            marker_colors=itertools.cycle([None])
        else:
            marker_colors = itertools.cycle(marker_colors)

        if line_colors is None: #defult color
            line_colors = itertools.cycle([None])
        else:
            line_colors = itertools.cycle(line_colors)

        styles=[dict() for i in range(n)]
        for i in range(n):
            m = next(markers)
            mc = next(marker_colors)
            if m is None:
                styles[i]['marker'] = 'none'
            else:
                styles[i].update(self.markers[m])
                if mc is None:
                    styles[i].update({'markeredgecolor': self.color,
                               'markerfacecolor': self.color})
                else:
                    if self.markers[m]['markeredgecolor'] != 'none':
                        styles[i]['markeredgecolor']= self.colors[mc]
                    if self.markers[m]['markerfacecolor'] != 'none':
                        styles[i]['markerfacecolor'] = self.colors[mc]

            d = next(dashes)
            if d is None:
                styles[i]['linestyle'] = 'None'
            else:
                styles[i]['dashes'] = self.dashes[d]

            lc = next(line_colors)
            if lc is None:
                styles[i]['color'] = self.color
            else:
                styles[i]['color'] = self.colors[lc]



        return styles




    def merge_default_markers(self):
        """Merge self.default_marker dict with each dict in self.markers"""
        self.markers=[copy_dict(self.default_marker, d) for d in self.markers]
        return

    def construct_dashes(self):
        """List of on, off tuples for use with matplotlib dashes"""

        self.dashes=[(None, None),
                     (10,3),
                     (3,4,10,4),
                     (2,2),
                     (10,4,3,4,3,4),
                     (10,10),
                    ]#, (7,3,7,3,7,3,2,3),(20,20) ,(5,5)]
        return

    def tint_colors(self, factor=1):
        "Lighten all colors by factor"

        self.colors = [rgb_tint(v, factor) for v in self.colors]
        return

    def shade_colors(self, factor=1):
        "Darken all colors by factor"

        self.colors = [rgb_shade(v, factor) for v in self.colors]
        return

    def construct_colors(self):
        """Populate self.colors: a list of rgb colors"""


        # These are from brewer2mpl.get_map('Set2', 'qualitative', 8).mpl_colors
            #see http://colorbrewer2.org/
        self.colors = [(0.4, 0.7607843137254902, 0.6470588235294118), #turqoise
                       (0.9882352941176471, 0.5529411764705883, 0.3843137254901961), #orange
                       (0.5529411764705883, 0.6274509803921569, 0.796078431372549), #blue
                       (0.9058823529411765, 0.5411764705882353, 0.7647058823529411), #pink
                       (0.6509803921568628, 0.8470588235294118, 0.32941176470588235), #lime green
#                       (1.0, 0.8509803921568627, 0.1843137254901961), # yellow
                       (0.8980392156862745, 0.7686274509803922, 0.5803921568627451), #light brown
                       (0.7019607843137254, 0.7019607843137254, 0.7019607843137254)] #grey

        self.shade_colors(0.8)

    def construct_markers(self):
        """Populate self.markers: a list of dict that define a matplotlib marker

        run `self.merge_default_markers` after running
        `self.construct_markers` so that default properties are applied
        properly.

        """

        #marker (numsides,style, angle) # theses markers cannot have fillstyle
        ngon=0
        star=1
        asterisk=2
        circle=3
        #fillstyle, 'full', 'left', 'right', 'bottom', 'top', 'none'

        #anything in self.makers
        self.markers=[
            #mix of matplotlib, named latex, and STIX font unicode
                # http://www.stixfonts.org/allGlyphs.html
            {'marker': 'o'},
            {'marker': 's',
             'fillstyle': 'bottom'},
            {'marker': 'D',
             'markerfacecolor': 'none'},
            {'marker': '^'},
            {'marker': 'o',
             'fillstyle': 'left'},
            {'marker': 's',
             'markerfacecolor': 'none'},
            {'marker': 'D',
             'fillstyle': 'top'},
            {'marker': '^',
             'fillstyle': 'left'},
            {'marker': 'o',
             'markerfacecolor': 'none'},
            {'marker': 's'},
            {'marker': 'D',
             'fillstyle': 'left'},
            {'marker': 'v',
             'markerfacecolor': 'none'},
            {'marker': r'$\boxplus$'},
            {'marker': 'D'},
            {'marker': 'v',
             'fillstyle': 'bottom'},
            {'marker': '^',
             'markerfacecolor': 'none'},
            {'marker': u'$\u25E9$'},
            {'marker': u'$\u2b2d$'},
            {'marker': 'h'},
            {'marker': '^',
             'fillstyle': 'bottom'},
            {'marker': r'$\otimes$'},
            {'marker': 'v'},
            {'marker': 'h',
             'fillstyle': 'right'},
            {'marker': 'o',
             'fillstyle': 'bottom'},
            {'marker': 's',
             'fillstyle': 'left'},
            {'marker': 'h',
             'markerfacecolor': 'none'},
            {'marker': 'H',
             'fillstyle': 'top'},
            {'marker': (6, asterisk, 0)},
            {'marker': u'$\u29bf$'},
            {'marker': u'$\u29c7$'},
            {'marker': u'$\u29fe$'},
            {'marker': u'$\u27E1$'},
            ]






#            #didn't make the cut
#            {'marker': 'H',
#             'fillstyle': 'bottom'},
#            {'marker': 'D',
#             'markerfacecolor': 'none',
#             'fillstyle': 'top'},
#            {'marker': 'o',
#             'markerfacecolor': 'none',
#             'fillstyle': 'top'},
#            {'marker': 's',
#             'markerfacecolor': 'none',
#             'fillstyle': 'top'},
#            {'marker': 'h',
#             'markerfacecolor': 'none',
#             'fillstyle': 'top'},
#            {'marker': '^',
#             'markerfacecolor': 'none',
#             'fillstyle': 'top'},
#
#            {'marker': '^',
#             'markerfacecolor': 'none',
#             'fillstyle': 'right'},
#            {'marker': 's',
#             'markerfacecolor': 'none',
#             'fillstyle': 'right'},
#            {'marker': 'o',
#             'markerfacecolor': 'none',
#             'fillstyle': 'right'},
#            {'marker': 'h',
#             'markerfacecolor': 'none',
#             'fillstyle': 'right'},
#            {'marker': 'D',
#             'markerfacecolor': 'none',
#             'fillstyle': 'right'},
#
#             #default matplotlib markers that didn't make the cut
#            {'marker': 0},
#            {'marker': 1},
#            {'marker': 2},
#            {'marker': 3},
#            {'marker': 4},
#            {'marker': 6},
#            {'marker': 7},
#            {'marker': '|'},
#            {'marker': ''},
#            {'marker': 'None'},
#            {'marker': None},
#            {'marker': 'x'},
#            {'marker': 5},
#            {'marker': '_'},
#            {'marker': ' '},
#            {'marker': 'd'},
#            {'marker': 'd',
#             'fillstyle': 'bottom'},
#            {'marker': 'd',
#             'fillstyle': 'left'},
#            {'marker': '+'},
#            {'marker': '*'},
#            {'marker': ','},
#            {'marker': '.'},
#            {'marker': '1'},
#            {'marker': 'p'},
#            {'marker': '3'},
#            {'marker': '2'},
#            {'marker': '4'},
#            {'marker': 'H'},
#            {'marker': 'v',
#             'fillstyle': 'left'},
#            {'marker': '8'},
#            {'marker': '<'},
#            {'marker': '>'},
#            {'marker': (6, star, 0)},

#            #named latex that didn't make the cut
#            {'marker': r'$\boxtimes$'},
#            {'marker': r'$\boxdot$'},
#            {'marker': r'$\oplus$'},
#            {'marker': r'$\odot$'},
#            {'marker': u'$\smile$'},

            #STIX FONTS unicode that didn't make the cut
#            {'marker': u'$\u29b8$'},
#            {'marker': u'$\u29bb$'},
#            {'marker': u'$\u29be$'},
#            {'marker': u'$\u29c4$'},
#            {'marker': u'$\u29c5$'},
#            {'marker': u'$\u29c6$'},
#            {'marker': u'$\u29c8$'},
#            {'marker': u'$\u29d0$'},
#            {'marker': u'$\u29d1$'},
#            {'marker': u'$\u29d2$'},
#            {'marker': u'$\u29d3$'},
#            {'marker': u'$\u29d6$'},
#            {'marker': u'$\u29d7$'},
#            {'marker': u'$\u29e8$'},
#            {'marker': u'$\u29e9$'},
#            {'marker': u'$\u2b12$'},
#            {'marker': u'$\u2b13$'},
#            {'marker': u'$\u2b14$'},
#            {'marker': u'$\u2b15$'},
#            {'marker': u'$\u2b16$'},
#            {'marker': u'$\u2b17$'},
#            {'marker': u'$\u2b18$'},
#            {'marker': u'$\u2b19$'},
#            {'marker': u'$\u2b1f$'},
#            {'marker': u'$\u2b20$'},
#            {'marker': u'$\u2b21$'},
#            {'marker': u'$\u2b22$'},
#            {'marker': u'$\u2b23$'},
#            {'marker': u'$\u2b24$'},
#            {'marker': u'$\u2b25$'},
#            {'marker': u'$\u2b26$'},
#            {'marker': u'$\u2b27$'},
#            {'marker': u'$\u2b28$'},
#            {'marker': u'$\u2b29$'},
#            {'marker': u'$\u2b2a$'},
#            {'marker': u'$\u2b2b$'},
#            {'marker': u'$\u2b2c$'},
#            {'marker': u'$\u2b2e$'},
#            {'marker': u'$\u2b2f$'},
#            {'marker': u'$\u272a$'},
#            {'marker': u'$\u2736$'},
#            {'marker': u'$\u273d$'},
#            {'marker': u'$\u27c1$'},
#            {'marker': u'$\u25A3$'},
#            {'marker': u'$\u25C8$'},
#            {'marker': u'$\u25D0$'},#strange straight ine on upper right
#            {'marker': u'$\u25D1$'},#strange straight ine on upper right
#            {'marker': u'$\u25D2$'},#strange straight ine on upper right
#            {'marker': u'$\u25D3$'},#strange straight ine on upper right
#            {'marker': u'$\u25E7$'},
#            {'marker': u'$\u25E8$'},
#            {'marker': u'$\u25EA$'},
#            {'marker': u'$\u25EC$'},
#            {'marker': u'$\u27D0$'},
#            {'marker': u'$\u2A39$'},
#            {'marker': u'$\u2A3B$'},
#            {'marker': u'$\u22C7$'},
#            {'marker': u'$\u$'},


    #matplotlib markers
    #marker 	description
    #"." 	point
    #"," 	pixel
    #"o" 	circle
    #"v" 	triangle_down
    #"^" 	triangle_up
    #"<" 	triangle_left
    #">" 	triangle_right
    #"1" 	tri_down
    #"2" 	tri_up
    #"3" 	tri_left
    #"4" 	tri_right
    #"8" 	octagon
    #"s" 	square
    #"p" 	pentagon
    #"*" 	star
    #"h" 	hexagon1
    #"H" 	hexagon2
    #"+" 	plus
    #"x" 	x
    #"D" 	diamond
    #"d" 	thin_diamond
    #"|" 	vline
    #"_" 	hline
    #TICKLEFT 	tickleft
    #TICKRIGHT 	tickright
    #TICKUP 	tickup
    #TICKDOWN 	tickdown
    #CARETLEFT 	caretleft
    #CARETRIGHT 	caretright
    #CARETUP 	caretup
    #CARETDOWN 	caretdown
    #"None" 	nothing
    #None 	nothing
    #" " 	nothing
    #"" 	nothing


        return



    def construct_styles(self, markers=None, dashes=None, marker_colors=None,
                         line_colors=None):
        """Calls self.__call__ and assigns results to self.styles"""

        self.styles = self(markers, dashes, marker_colors, line_colors)

        return

    def demo_styles(self):
        """Show a figure of all the styles in self.styles"""

        fig = plt.figure(figsize=(10,10))
        ax = fig.add_subplot(111, frame_on=True)
        ax.get_xaxis().set_ticks([])
        ax.get_yaxis().set_ticks([])

        if len(self.styles)==0:
            ax.set_title("No styles set.  Use the 'construct_styles' method.")
        else:
            for i, style in enumerate(self.styles):
                x = (i % 5)*2
                y = i//5
                ax.plot(np.array([x,x+1]), np.array([y,y+0.3]), **style)
                s=i
                ax.annotate(s, xy=(x+1,y+0.3),
                             xytext=(18, 0), textcoords='offset points',
                             horizontalalignment='left', verticalalignment='center')
            ax.set_xlim(-1, 11)
            ax.set_ylim(-1, y+1)
            ax.set_xlabel('styles')

        plt.show()
        return

    def demo_options(self):
        """Show a figure with all the marker, dashes, color options available"""

        #markers
        gs = gridspec.GridSpec(3,1)
        fig=plt.figure(num=1,figsize=(12,10))


        ax1=fig.add_subplot(gs[0])
        for i, m in enumerate(self.markers):
            x = (i % 5)*2
            y = i//5
            ax1.plot(np.array([x,x+1]), np.array([y,y+0.3]), **m)
            s=repr(m['marker']).replace('$','').replace("u'\\u","")
            s=i
            ax1.annotate(s, xy=(x+1,y+0.3),
                         xytext=(18, 0), textcoords='offset points',
                         horizontalalignment='left', verticalalignment='center')
        ax1.set_xlim(-1, 11)
        ax1.set_ylim(-1, y+1)
        ax1.set_xlabel('Markers')
        ax1.get_xaxis().set_ticks([])
        ax1.get_yaxis().set_ticks([])
        ax1.set_title('Options for MarkersDashesColors object')

        #dashes
        ax2=fig.add_subplot(gs[1])
        for i, d in enumerate(self.dashes):
            x = 0
            y = i
            ax2.plot(np.array([x,x+1]), np.array([y,y+0.3]), dashes=d,color=self.almost_black)
            s=i
            ax2.annotate(s, xy=(x+1,y+0.3),
                         xytext=(18, 0), textcoords='offset points',
                         horizontalalignment='left', verticalalignment='center',
                         color = self.almost_black
                         )
        ax2.set_xlim(-0.1,1.2)
        ax2.set_ylim(-1,y+1)
        ax2.set_xlabel('Dashes')
        ax2.get_xaxis().set_ticks([])
        ax2.get_yaxis().set_ticks([])

        #colors
        ax3 = fig.add_subplot(gs[2])
        for i, c in enumerate(self.colors):
            x = 0
            y = i
            ax3.plot(np.array([x,x+1]), np.array([y,y+0.3]), color=c,ls='-')
            s=i
            ax3.annotate(s, xy=(x+1,y+0.3),
                         xytext=(18, 0), textcoords='offset points',
                         horizontalalignment='left', verticalalignment='center',
                         color=self.almost_black
                         )
        ax3.set_xlim(-0.1,1.2)
        ax3.set_ylim(-1,y+1)
        ax3.set_xlabel('colors')
        ax3.get_xaxis().set_ticks([])
        ax3.get_yaxis().set_ticks([])

        plt.show()
        return


def pleasing_defaults():
    """Alter some matplotlib rcparams defaults to be visually more appealing


    References
    ----------
    Many of the ideas/defaults/code come from Olga Botvinnik [1]_, and her
    `prettyplot` package [2]_.

    .. [1] http://blog.olgabotvinnik.com/post/58941062205/prettyplotlib-painlessly-create-beautiful-matplotlib
    .. [2] http://olgabot.github.io/prettyplotlib/

    """


    # Get Set2 from ColorBrewer, a set of colors deemed colorblind-safe and
    # pleasant to look at by Drs. Cynthia Brewer and Mark Harrower of Pennsylvania
    # State University. These colors look lovely together, and are less
    # saturated than those colors in Set1. For more on ColorBrewer, see:
    # - Flash-based interactive map:
    #     http://colorbrewer2.org/
    # - A quick visual reference to every ColorBrewer scale:
    #     http://bl.ocks.org/mbostock/5577023
    set2 = brewer2mpl.get_map('Set2', 'qualitative', 8).mpl_colors

    # Another ColorBrewer scale. This one has nice "traditional" colors like
    # reds and blues
    set1 = brewer2mpl.get_map('Set1', 'qualitative', 9).mpl_colors
    mpl.rcParams['axes.color_cycle'] = set2

    # Set some commonly used colors
    almost_black = '#262626'
    light_grey = np.array([float(248) / float(255)] * 3)

    reds = mpl.cm.Reds
    reds.set_bad('white')
    reds.set_under('white')

    blues_r = mpl.cm.Blues_r
    blues_r.set_bad('white')
    blues_r.set_under('white')

    # Need to 'reverse' red to blue so that blue=cold=small numbers,
    # and red=hot=large numbers with '_r' suffix
    blue_red = brewer2mpl.get_map('RdBu', 'Diverging', 11,
                                  reverse=True).mpl_colormap

    # Default "patches" like scatterplots
    mpl.rcParams['patch.linewidth'] = 0.75     # edge width in points

    # Default empty circle with a colored outline
    mpl.rcParams['patch.facecolor'] = 'none'
    mpl.rcParams['patch.edgecolor'] = set2[0]

    # Change the default axis colors from black to a slightly lighter black,
    # and a little thinner (0.5 instead of 1)
    mpl.rcParams['axes.edgecolor'] = almost_black
    mpl.rcParams['axes.labelcolor'] = almost_black
    mpl.rcParams['axes.linewidth'] = 0.5

    # Make the default grid be white so it "removes" lines rather than adds
    mpl.rcParams['grid.color'] = 'white'

    # change the tick colors also to the almost black
    mpl.rcParams['ytick.color'] = almost_black
    mpl.rcParams['xtick.color'] = almost_black

    # change the text colors also to the almost black
    mpl.rcParams['text.color'] = almost_black


def iterable_method_call(iterable, method, unpack, *args):
    """Call a method on each element of an iterable


    iterable[i].method(arg)

    Parameters
    ----------
    iterable : sequence etc.
        Iterable whos members will have thier attribute changed.
    method : string
        Method to call.
    unpack : bool
        If True then each member of `*args` will be unpacked before passing to
        method.
    *args : positional arguments
        If a single positional argument then all members of `iterable`
        will have their method called with the same single argument.
        If more that one positional argument then
        iterable[0].method will be called with args[0],
        iterable[1].method will be set to args[1] etc.
        Skip elements by having corresponding value of *args=None.

    """

    if len(args)==0:
        for i in iterable:
            getattr(i, method)()
        return
    if len(args)==1:
        if not args[0] is None:
            if unpack:
                for i in iterable:
                    getattr(i, method)(*args[0])
            else:
                for i in iterable:
                    getattr(i, method)(args[0])
        return
    if len(args)>1:
        for i, a in enumerate(args):
            if unpack:
                if not a is None:
                    getattr(iterable[i],method)(*a)
            else:
                if not a is None:
                    getattr(iterable[i],method)(a)
        return




def xylabel_subplots(fig, y_axis_labels=None, x_axis_labels=None):
    """Set x-axis label and y-axis label for each sub plot in figure

    Note: labels are applied to axes in the order they were created, which
    is not always the way they appear in the figure.

    Parameters
    ----------
    fig : matplotlib.Figure
        Figure to apply labels to.
    y_axis_labels : sequence
        Label to place on y-axis of each subplot.  Use None to skip a subplot.
        Default y_axis_label=None
    x_axis_labels : sequence
        Label to place on x-axis of each subplot.  Use None to skip a subplot.
        Default x_axis_label=None.


    """

    if not y_axis_labels is None:
        for i, label in enumerate(y_axis_labels):
            if not label is None:
                fig.axes[i].set_ylabel(label)
    if not x_axis_labels is None:
        for i, label in enumerate(x_axis_labels):
            if not label is None:
                fig.axes[i].set_xlabel(label)

    return


def row_major_order_reverse_map(shape, index_steps=None, transpose=False):
    """Map an index to a position in a row-major ordered array by reversing dims

    ::

         e.g. shape=(3,3)
         |2 1 0|      |0 1 2|
         |5 4 3| -->  |3 4 5|
         |8 7 6|      |6 7 8|
         need 0-->2, 1-->1, 2-->0. i.e. [2 1 0 5 4 3 8 7 6].
         Use row_major_order_reverse_map((3,3), (1,-1))


    Use this to essentially change the subplot ordering in a matplotlib figure.
    Say I wanted sub_plot ordering as in the left arrangement of the above
    example. use mymap = row_major_order_reverse_map((3,3), (1,-1)).  If I
    wanted to plot in my position 5 I would pass mymap[5] to the figure.



    Parameters
    ----------
    shape : tuple
        Shape of array, e.g. (rows, columns)
    index_steps : list of 1 or -1, optional
        Traverse each array dimension in steps f `index_steps`.
        Default index_steps=None i.e. all dims traversed in normal
        order. e.g. for 3 d array, index_steps=(1,-1, 1) would mean
        2nd dimension would be reversed.
    transpose : True/False, optional
        When True, transposes indexes (final operation).
        Default transpose=False.

    Returns
    -------
    pos : 1d ndarray
        Array that maps index to position in row-major ordered array

    Notes
    -----
    A use for this is positioning subplots in a matplotlib gridspec

    Examples
    --------
    >>> row_major_order_reverse_map(shape=(3, 3), index_steps=None, transpose=False)
    array([0, 1, 2, 3, 4, 5, 6, 7, 8])
    >>> row_major_order_reverse_map(shape=(3, 3), index_steps=(-1, 1), transpose=False)
    array([6, 7, 8, 3, 4, 5, 0, 1, 2])
    >>> row_major_order_reverse_map(shape=(3, 3), index_steps=(1, -1), transpose=False)
    array([2, 1, 0, 5, 4, 3, 8, 7, 6])
    >>> row_major_order_reverse_map(shape=(3, 3), index_steps=(-1, -1), transpose=False)
    array([8, 7, 6, 5, 4, 3, 2, 1, 0])
    >>> row_major_order_reverse_map(shape=(3, 3), index_steps=None, transpose=True)
    array([0, 3, 6, 1, 4, 7, 2, 5, 8])

    """
    shape=np.asarray(shape)
    if index_steps is None:
        index_steps=np.ones_like(shape,dtype=int)


    pos=np.arange(np.product(shape)).reshape(shape)
    a=[slice(None,None,i) for i in index_steps]
    pos[...]=pos[a]

    if transpose:
        return pos.T.flatten()
    else:
        return pos.flatten()


    return



def split_sequence_into_dict_and_nondicts(*args):
    """Separate dict and non-dict items. Merge dicts and merge non-dicts

    Elements are combined in the order that they appear.  i.e. non-dict items
    will be appended to a combined list as they are encounterd.  Repeated dict
    keys will be overridded by the latest value.

    Parameters
    ----------
    *args : one or more positional items
        Mixture of dict and non-dict.

    Returns
    -------
    merged_non_dict : list
        List of non dictionary items.
    merged_dict : dict
        Merged dictionary.

    """


    merged_non_dict=[]
    merged_dict=dict()

    for v in args:
        if isinstance(v, dict):
            merged_dict.update(v) #http://stackoverflow.com/a/39437/2530083
        else:
            merged_non_dict.append(v)
    return merged_non_dict, merged_dict


def plot_data_in_grid(fig, data, gs,
                       gs_index=None,
                       sharex=None, sharey=None):
    """Make a subplot for each set of data

    Parameters
    ----------
    fig : matplotlib.Figure
        Figure to create subplots in.
    data : sequence of sequence of 2 element sequence
        data[i] = Data for the ith subplot.
        data[i][j] = jth (x, y) data set for the ith subplot.
        Each set of (x, y) data will be plotted using matplotlib.plot fn
        e.g. data=[([x0, y0],), ([x1, y1],), ([x2a, y2a], [x2b, x2b])]
        Note that data[i][j] will be split into list of all the non-dict items
        and a merged dict of all the dict items.  Both the list and the merged
        dict will be unpacked and passed to the `plot_type` function.  This
        allows passing of keyword arguments. If one of the dict keys is
        'plot_type' it's value should be a string indicating a method of
        matplotlib.Axes that can be used to create the subplot.  If
        'plot_type' is not found then the default matplotlib.Axes.plot will
        be used. Be careful when using () to group data if there is only
        one item in the (item) then they are just parentheses and you are
        just saying 'item'; put a comma after the item to make it a tuple
        which is usually what you want when specifying data in this function.
    gs : matplotlib.gridspec.GridSpec instance
        Defines the grid in which subplots will be created.
    gs_index : List of int or list of slice, optional
        Specifies the position within gs that each data set will be plotted
        Positions can be specified by 1) an integer which will correspond to
        row-major ordering in the grid (e.g. for a 3x3 grid, index 3 will be
        second row, first column), or 2) a tuple of (row,column), or 3) a slice
        (e.g. index of np.s_[:1,:1] will span from first row, first column to
        second row, second column).  Another slice method is slice(3,7) which
        will span from position 3 to position 7.
        Default gs_index=None subplots are added in row-major ordering.
    sharex : sequence of int
        Subplot index to share x-axis with.
        Default sharex=None i.e. no sharing.
        To skip a  subplot put None as the corresponding element of sharex.
        If only one value is given and ther is more than one data set then
        all subplots will share the given axis.  Note that the axis to share
        must already have been created.
    sharey : sequence of int
        Subplot index to share y-axis with.
        Default sharey=None i.e. no sharing.
        To skip a  subplot put None as the corresponding element of sharey.
        If only one value is given and ther is more than one data set then
        all subplots will share the given axis.  Note that the axis to share
        must already have been created.


    Returns
    -------
    ax : List of :class:`matplotlib.pyplot.Axes` instances. Don't be
        confused with normal meaning of 'ax', this `ax` is a list of Axes, not
        just one.

    Notes
    -----
    You may be wondering how to apply axes labels and such.  Do something like
    [a.set_xlabel(v) for a, v in zip(fig.get_axes(), [xlabel1, xlabel2, ...])]


    """

#    gridspec_prop: dict
#        dictionary of keyword arguments to pass to matplotlib.gridspec.GridSpec
#        object. Any attribute will correspond to the convential positioning,
#        i.e. gs_index will be ignored. Default=dict().
#        e.g. gridspec_prop=dict(width_ratios=[1,2],
#        height_ratios=[4,1], left=0.55, right=0.98, hspace=0.05, wspace=0.02)
#    plot_type: sequence of str, optional
#        list of matplotlib.pyplot methods to use for each data set.
#        default=None which uses 'plot'
#        i.e. x-y plot.  e.g. plot_type='scatter' gives a scatter plot.

    if gs_index is None:
        gs_index = np.arange(len(data))

#    if plot_type is None:
#        plot_type = ['plot' for i in data]
#    elif len(plot_type) == 1:
#        plot_type = [plot_type[0] for i in data]


    if sharex is None:
        sharex = [None for i in data]
    elif len(sharex) == 1:
        i = sharex[0]
        sharex = [i for j in data]
        sharex[i] = None

    if sharey is None:
        sharey = [None for i in data]
    elif len(sharey) == 1:
        i = sharey[0]
        sharey = [i for j in data]
        sharey[i] = None

    ax = []
    for i, subplot_data in enumerate(data):
        #subplot_data is all [x,y,dict] for each subplot
        j = gs_index[i]
        if sharex[i] is None:
            shx=None
        else:
            shx=ax[sharex[i]]

        if sharey[i] is None:
            shy=None
        else:
            shy=ax[sharey[i]]

        ax.append(fig.add_subplot(gs[j]))

        for j, xy_etc in enumerate(subplot_data):
            #xy_etc is a single [x,y,dict] to send to plt.plot, or plt.plot_type
            args_, kwargs_ = split_sequence_into_dict_and_nondicts(*xy_etc)
            plot_type = kwargs_.pop('plot_type', 'plot')

            getattr(ax[-1], plot_type)(*args_,**kwargs_) #http://stackoverflow.com/a/3071/2530083





#        if suplot_data is None:
#            ax[-1].plot()
##            getattr(ax[-1], plot_type[i])()
##            ax[-1].axis('off')#removes axes instance
#            ax[-1].set_axis_bgcolor('none')
#            ax[-1].set_frame_on(False)
#            ax[-1].get_xaxis().set_ticks([])#http://stackoverflow.com/a/2176591/2530083
#            ax[-1].get_yaxis().set_ticks([])
#        else:
#
##        ax[-1].set_ylabel(i) #use for debugging
    return ax

def apply_dict_to_object(obj, dic):
    """Apply a dict of properties to a matplotlib object.

    Note the object must support set_<property_name> methods
    If obj and d are lists then the each `dic` will be applied to the
    corresponding `obj`.

    Parameters
    ----------
    obj : matplotlib object or list of
        Object to set properties in.  Typically a matplotlib.lines.Line2D
        instance.
    dic : dict or list of dict
        A dictionary or properties to apply to the object. e.g for a
        matplotlib.lines.Line2D dict keys might be 'marker', or
        'linestyle' etc.  i.e any kwarg you would pass to plt.plot.
        Note that if a key in dic does not correspond to a obj.set_key
        method then it will be ignored.


    """

    if not isinstance(obj, list):
        obj = [obj]

    if not isinstance(dic, list):
        dic = [dic]


    if len(obj)!=len(dic):
        raise ValueError('obj and d must be the same lenght. {} vs '
        '{}'.format(len(obj), len(dic)))

    for o, d in zip(obj, dic):
        if d is None:
            continue
        for key, value in d.items():
            s = 'set_{0}'.format(key)
            if hasattr(o, s):
                getattr(o, s)(value)

    return

def plot_generic_loads(load_triples, load_names, ylabels=None,
                        trange = None, H = 1.0, RLzero=None, prop_dict={}):
    """Plot loads that come in load_vs_time-load_vs_depth-omega_phase form

    For each load_triple (i.e. each load type) two plots will be made
    side by side: a load_vs_time plot; and a load_vs_depth plot. the
    different load types will appear one under the other.

    ::
        Load Magnitude                 Depth
        ^                              ^
        |           .....               |     *
        |          .                    |    *
        |   . . . .                     |   *
        |  .                            |   *
        | .                             |    *
        --------------------->Time     --------->Load factor


    Parameters
    ----------
    load_triples : list of list of 3 element tuples
        (load_vs_time, load_vs_depth, load_omega_phase) PolyLines.
        load_triples[i] will be a list of load triples for the ith plot
        load_triples[i][j] will be the jth load triple for the ith plot.
        The load_vs_depth can also be a two element tuple containing a
        list/array of depth values and a list/array of load values.
        The load_vs_time can also be a two element tuple containing a
        list/array of time values and a list/array of load values.
    load_names : list of string
        string to prepend to legend entries for each load
    ylabels : list of string, optional
        y labels for each of the axes, Default ylabels=None
        i.e. y0, y1, y2 etc.
    trange : 2 element tuple, optional
        (tmin, tmax) max and min times to plot loads for. Default trange=None
        i.e. t limits will be worked out from data.
    H : float, optional
        Height of soil profile.  Default H=1.0.  Used to transform
        normalised depth to actual depth.
    RLzero : float, optional
        Reduced level of the top of the soil layer.  If RLzero is not None
        then all depths (in plots and results) will be transformed to an
        RL by RL = RLzero - z*H.  If RLzero is None (i.e. the default)
        then all actual depths will be reported z*H (i.e. positive numbers).
    prop_dict : dict of dict, optional
        Dictionary containing certain properties used to set various plot
        options.

        ==================  ============================================
        prop_dict option    description
        ==================  ============================================
        fig_prop            dict of prop to pass to plt.figure.
                            Defaults include:
                            figsize=(7.05, 1.57 * no.of.loads)
        styles              List of dict.  Each dict is for one line.
                            Each dict contains kwargs for plt.plot.
                            SeeMarkersDashesColors. Defaults give black
                            and white markersize 5.
        time_axis_label     Label for x axis in load_vs_time plots.
                            Default='Time'
        depth_axis_label    Label for y axis in load_vs_depth plot
                            Default="Depth, z" or "RL" depending on
                            RLzero.
        has_legend          True or False. Default = True.
        legend_prop         dict of prop to pass to ax.legend.
                            Defaults include:
                            title='Load'
                            fontsize=9
        ==================  ============================================


    Returns
    -------
    fig : matplolib.Figure
        Figure with plots.


    """


    fig_prop = copy_dict({'figsize':(18/2.54, (18/1.61/2.54)/ 2.8 *len(load_triples))},
                          prop_dict.get('fig_prop', {}))
#    fig_prop = prop_dict.get('fig_prop', {'figsize':(18/2.54, (18/1.61/2.54)/ 2.8 *len(load_triples)) })
    legend_prop = copy_dict({'title': 'Load:', 'fontsize': 9},
                            prop_dict.get('legend_prop',{}))
#    legend_prop = prop_dict.get('legend_prop',
#                               {'title': 'Load:', 'fontsize': 9})

    styles = prop_dict.get('styles', None)
    if styles is None:
        mcd = MarkersDashesColors(
            #color = 'black',
            markersize= 7)
        mcd.construct_styles(markers = list(range(32)), dashes=[0],
                             marker_colors=None, line_colors=None)


        styles = itertools.cycle(mcd.styles)
    else:
        styles = itertools.cycle(styles)

    has_legend = prop_dict.get('has_legend', True)
    xlabel1 = prop_dict.get('time_axis_label', 'Time')
    xlabel2 = prop_dict.get('depth_axis_label', 'Load factor')
    n = len(load_triples)

    gs = mpl.gridspec.GridSpec(n,2, width_ratios=[5,1])
    fig = plt.figure(**fig_prop)

    #plt.subplot(gs[0])

    if ylabels is None:
        ylabels = ['y{:d}'.format(v) for v in range(n)]

    #determine tmax, tmin
    if trange is None:
        for i, (triples, name, ylabel)  in enumerate(zip(load_triples, load_names, ylabels)):
            for j, (vs_time, vs_depth, omega_phase) in enumerate(triples):
                if i==0 and j==0:
                    tmin = np.min(vs_time.x)
                    tmax = np.max(vs_time.x)
                else:
                    tmin = min(tmin, np.min(vs_time.x))
                    tmax = max(tmax, np.max(vs_time.x))
    else:
        tmin, tmax = trange





    ax1 = []
    ax2 = []
    for i, (triples, name, ylabel)  in enumerate(zip(load_triples, load_names, ylabels)):

        sharex1 = None
        sharex2 = None
        sharey1 = None
        sharey2 = None
        if i != 0:
            sharex1 = ax1[0]
            sharex2 = ax2[0]
            sharey1 = ax1[0]
            sharey2 = ax2[0]
        ax1.append(plt.subplot(gs[i, 0], sharex=sharex1, sharey=sharey1))
        ax2.append(plt.subplot(gs[i, 1], sharex=sharex2, sharey=sharey2 ))

        for j, (vs_time, vs_depth, omega_phase) in enumerate(triples):
            style = next(styles)
            if vs_time is None: #allow for fixed ppress
                vs_time = PolyLine([tmin, tmax], [0.0, 0.0])

            if not isinstance(vs_time, PolyLine):
                x_, y_ =vs_time
                vs_time = PolyLine(x_,y_)


            dx = (tmax-tmin)/20.0

            if not omega_phase is None:
                omega, phase = omega_phase
                dx = min(dx, 1/(omega/(2*np.pi))/40)


#                print(dx, omega)

#            x = [np.linspace(x1, x2, max(int((x2-x1)//dx), 4)) for
#                    (x1, x2, y1, y2) in zip(vs_time.x[:-1], vs_time.x[1:], vs_time.y[:-1], vs_time.y[1:])]
#                    #if abs(y2-y1) > 1e-5 and abs(x2-x1) > 1e-5]
#
#            y = [np.linspace(y1, y2, max(int((x2-x1)//dx), 4)) for
#                    (x1, x2, y1, y2) in zip(vs_time.x[:-1], vs_time.x[1:], vs_time.y[:-1], vs_time.y[1:])]
#                    #if abs(y2-y1) > 1e-5 and abs(x2-x1) > 1e-5]
#
#            x = np.array([val for subl in x for val in subl])
#            y = np.array([val for subl in y for val in subl])
            x, y = pwise.subdivide_x_y_into_segments(x=vs_time.x, y=vs_time.y, dx=dx, min_segments=4)
            if not omega_phase is None:
                y *= np.cos(omega * x + phase)




            linename = name + str(j)

#            ax1[-1].plot(x, y, label=linename, markevery=markevery, **style)
            ax1[-1].plot(x, y, label=linename, **style)
            apply_markevery_to_sequence_of_lines(ax1[-1].get_lines(),
                                         markevery=0.1,
                                         random_start=True, seed=1)
#            try:
#                random.seed(1)
#                [apply_dict_to_object(line, d)
#                    for line, d in
#                        zip(ax1[-1].get_lines(),
#                            [{'markevery': (random.random()* 0.1, 0.1)} for v in ax1[-1].get_lines()])]
#            except ValueError:
#                pass
            #TODO: add some more points in the z direction, account for when only one point

            if isinstance(vs_depth, PolyLine):
                dx = (np.max(vs_depth.x)-np.min(vs_depth.x))/8

#                x = [np.linspace(x1, x2, max(int((x2-x1)//dx), 4)) for
#                        (x1, x2, y1, y2) in zip(vs_depth.x[:-1], vs_depth.x[1:], vs_depth.y[:-1], vs_depth.y[1:])]
#                        #if abs(y2-y1) > 1e-5 and abs(x2-x1) > 1e-5]
#
#                y = [np.linspace(y1, y2, max(int((x2-x1)//dx), 4)) for
#                        (x1, x2, y1, y2) in zip(vs_depth.x[:-1], vs_depth.x[1:], vs_depth.y[:-1], vs_depth.y[1:])]
#
#                x = np.array([val for subl in x for val in subl])
#                y = np.array([val for subl in y for val in subl])
                x, y = pwise.subdivide_x_y_into_segments(x=vs_depth.x, y=vs_depth.y, dx=dx, min_segments=4)
            else: # assume a tuple of x and y values
                    x, y = vs_depth
                    x = np.atleast_1d(x)
                    y = np.atleast_1d(y)
            z = transformations.depth_to_reduced_level(x, H, RLzero)
            ax2[-1].plot(y, z, label=linename, **style)



        #load_vs_time plot stuff

        if i==len(load_triples)-1:
            ax1[-1].set_xlabel(xlabel1)
        ax1[-1].set_ylabel(ylabel)

        if not trange is None:
            ax1[-1].set_xlim((tmin, tmax))



        if has_legend:
            leg = ax1[-1].legend(**legend_prop)
            leg.draggable(True)
            plt.setp(leg.get_title(),fontsize=legend_prop['fontsize'])
        #load_vs_depth plot stuff

        if i==len(load_triples)-1:
            ax2[-1].set_xlabel(xlabel2)

        if RLzero is None:
            ax2[-1].invert_yaxis()
            ylabel = prop_dict.get('depth_axis_label', 'Depth, z')
        else:
            ylabel = prop_dict.get('depth_axis_label', 'RL')

        ax2[-1].set_ylabel(ylabel)
        ax2[-1].set_xlim((0,1.01))
        ax2[-1].set_xticks([0,0.5,1])

        fig.tight_layout()
    return fig


def plot_vs_time(t, y, line_labels=None, prop_dict={}):
    """Plot y vs t with some options

    Originally used for plotting things like average excess pore pressure
    vs time.

    ::

        y
        ^
        |           .......
        |          .
        |   . . . .  ***
        |  . *      *   *
        | .*   *****
        --------------------->Time

    Parameters
    ----------
    t : np.array
        Time values.
    y :  one or two dimensional ndarray
        y values to plot.  basically plt.plot(t,y) will be used.
    line_labels : list of string, optional
        Label for each line in y.  Defaultline_labels=None, i.e. no labels.
    prop_dict : dict of dict, optional
        Dictionary containing certain properties used to set various plot
        options.

        ==================  ============================================
        prop_dict option    description
        ==================  ============================================
        fig_prop            dict of prop to pass to plt.figure.
                            Defaults include:
                            figsize=(7.05, 4.4)
        styles              List of dict.  Each dict is for one line.
                            Each dict contains kwargs for plt.plot
                            See
                            MarkersDashesColors
                            defaults give black and white markersize 5
        xlabel              x-axis label. default='Time'.
        ylabel              y-axis label. default = 'y'.
        has_legend          True or False. default = True.
        legend_prop         dict of prop to pass to ax.legend
                            Defaults include:
                            title='Depth interval'
                            fontsize=9
        ==================  ============================================

    Returns
    -------
    fig : matplolib.Figure
        Figure with plots.


    """

    fig_prop = copy_dict({'figsize':(18/2.54, 18/1.61/2.54)},
                          prop_dict.get('fig_prop', {}))

#    fig_prop = prop_dict.get('fig_prop', {'figsize':(18/2.54, 18/1.61/2.54)})

    legend_prop = copy_dict({'title': 'Depth interval:', 'fontsize': 9},
                            prop_dict.get('legend_prop',{}))

#    legend_prop = prop_dict.get('legend_prop',
#                               {'title': 'Depth interval:', 'fontsize': 9})

    styles = prop_dict.get('styles', None)
    if styles is None:
        mcd = MarkersDashesColors(
            #color = 'black',
            markersize= 7)
        mcd.construct_styles(markers = list(range(32)), dashes=[0],
                             marker_colors=None, line_colors=None)


        styles = itertools.cycle(mcd.styles)
    else:
        styles = itertools.cycle(styles)



    #z = transformations.depth_to_reduced_level(z, H, RLzero)

    #t = self.tvals[self.ppress_z_tval_indexes]


    fig = plt.figure(**fig_prop)
    plt.plot(t, y)

    xlabel = prop_dict.get('xlabel', 'Time, t')
    plt.xlabel(xlabel)
    ylabel = prop_dict.get('ylabel', 'y')
    plt.ylabel(ylabel)

    #apply style to each line
    [apply_dict_to_object(line, d)
        for line, d in zip(fig.gca().get_lines(), styles)]
    #apply markevery to each line
    apply_markevery_to_sequence_of_lines(fig.gca().get_lines(),
                                         markevery=0.1,
                                         random_start=True, seed=1)
#    try:
#        random.seed(1)
#        [apply_dict_to_object(line, d)
#            for line, d in
#                zip(fig.gca().get_lines(),
#                    [{'markevery': (random.random()* 0.1, 0.1)} for v in y])]
#    except ValueError:
#        pass

    if (not line_labels is None):
        labels = [{'label': v} for v in line_labels]
        [apply_dict_to_object(line, d)
            for line, d in zip(fig.gca().get_lines(), labels)]
        has_legend = prop_dict.get('has_legend', True)
    else:
        has_legend=False

    if has_legend:
        leg = fig.gca().legend(**legend_prop)
        leg.draggable(True)
        plt.setp(leg.get_title(),fontsize=legend_prop['fontsize'])
    return fig


def plot_single_material_vs_depth(z_x, xlabels, H = 1.0, RLzero=None,
                    prop_dict={}):
    """Plot side by side property vs depth graphs

    ::

        x1           x2           x3
        -----------> -----------> ------------>
        |     .      |   .        |   .        |
        |     .      |    .       |  .         |
        |     .      |     .      |  .         |
        |    .       |      .     |    .       |
        |   .        |      .     |      .     |
        |  .         |      .     |        .   |
        v            v            v
        depth

    Parameters
    ----------
    z_x : list of PolyLine
        List of value_vs_depth PolyLines.
    xlabels : list of string
        List of x-axis labels.
    H : float, optional
        Height of soil profile.  Default H=1.0.  Used to transform
        normalised depth to actual depth.
    RLzero : float, optional
        Reduced level of the top of the soil layer.  If RLzero is not None
        then all depths (in plots and results) will be transformed to an
        RL by RL = RLzero - z*H.  If RLzero is None (i.e. the default)
        then all depths will be reported  z*H (i.e. positive numbers).
    prop_dict : dict of dict, optional
        Dictionary containing certain properties used to set various plot
        options:

        ==================  ============================================
        prop_dict option    description
        ==================  ============================================
        fig_prop            dict of prop to pass to plt.figure.
                            defaults include:
                            figsize=(7.05, 4.4)
        styles              List of dict.  Each dict is for one line.
                            Each dict contains kwargs for plt.plot
                            See
                            MarkersDashesColors
                            defaults give black and white markersize 5
        xlabel              x-axis label. default = 'Time'
        ylabel              y-axis label. default = 'Depth, z' or 'RL'
                            depending on RLzero.
        ==================  ============================================


    """


    n = len(z_x)

    fig_prop = copy_dict({'figsize':(2 * n, 18/1.61/2.54)},
                          prop_dict.get('fig_prop', {}))

#    fig_prop = prop_dict.get('fig_prop', {'figsize':(2 * n, 18/1.61/2.54)})

    styles = prop_dict.get('styles', None)
    if styles is None:
        mcd = MarkersDashesColors(
            #color = 'black',
            markersize= 7)
        mcd.construct_styles(markers = list(range(32)), dashes=[0],
                             marker_colors=None, line_colors=None)


        styles = itertools.cycle(mcd.styles)
    else:
        styles = itertools.cycle(styles)


    gs = mpl.gridspec.GridSpec(1,n, width_ratios=None, wspace=0.13)
    gs.update(left=0.1, right=0.98, bottom=0.05,  top=0.9)
    fig = plt.figure(**fig_prop)

    ax1=[]
    style = next(styles)
    for i, (vs_depth, xlabel)  in enumerate(zip(z_x, xlabels)):


        sharey1 = None
        if i != 0: #share the y axis
            sharex1 = ax1[0]
            sharey1 = ax1[0]

        ax1.append(plt.subplot(gs[i], sharey=sharey1))

        if not isinstance(vs_depth, PolyLine):
            # assume a tuple of x and y values
            x_, y_ =vs_depth
            vs_depth = PolyLine(x_,y_)

        dx = (np.max(vs_depth.x)-np.min(vs_depth.x)) / 8
#
#        x = [np.linspace(x1, x2, max(int((x2-x1)//dx), 4)) for
#                (x1, x2, y1, y2) in zip(vs_depth.x[:-1], vs_depth.x[1:], vs_depth.y[:-1], vs_depth.y[1:])]
#                #if abs(y2-y1) > 1e-5 and abs(x2-x1) > 1e-5]
#
#        y = [np.linspace(y1, y2, max(int((x2-x1)//dx), 4)) for
#                (x1, x2, y1, y2) in zip(vs_depth.x[:-1], vs_depth.x[1:], vs_depth.y[:-1], vs_depth.y[1:])]
#
#        x = np.array([val for subl in x for val in subl])
#        y = np.array([val for subl in y for val in subl])

        x, y = pwise.subdivide_x_y_into_segments(x=vs_depth.x, y=vs_depth.y, dx=dx, min_segments=4)
        z = transformations.depth_to_reduced_level(x, H, RLzero)
        ax1[-1].plot(y, z, **style)


        ax1[-1].set_xlabel(xlabel, multialignment='center')
        ax1[-1].xaxis.set_label_position('top')
        ax1[-1].xaxis.tick_top()

        ax1[-1].xaxis.set_major_locator( plt.MaxNLocator(4))
        ax1[-1].xaxis.set_minor_locator( plt.AutoLocator())
        cur_xlim = ax1[-1].get_xlim()

        ax1[-1].set_xlim([0, cur_xlim[1]])



        #ax1[-1].xaxis.set_minor_locator(ml)

        #ax1[-1].set_xticks(ax1[-1].get_xticks()[1:])




        if i != 0:
            #ax1[-1].yaxis.set_ticklabels([])
            plt.setp(ax1[-1].get_yticklabels(), visible=False)


    if RLzero is None:
        plt.gca().invert_yaxis()
        ylabel = prop_dict.get('ylabel', 'Depth, z')
    else:
        ylabel = prop_dict.get('ylabel', 'RL')
    ax1[0].set_ylabel(ylabel)
    #ax1[-1].yaxis.set_ticklabels([])

    #fig.tight_layout()
    return fig


def apply_markevery_to_sequence_of_lines(lines, markevery=None ,
                                         random_start=True, seed=None):
    """Apply `markevery` property to sequence of matplotlib lines

    Allows for a random start so that marker on different lines do not
    line up.

    Parameters
    ----------
    lines : sequence of matplotlib lines
        Lines to apply markevery to.
    markevery : int or float, optional
        Value of markevery property. Default markevery=None, i.e.
        markevery will be turned off and all points will have markers.
    random_start : True/False
        If True then first marker shown will be random between start marker
        and the markevery property. Default random_start=True.
    seed : int, optional
        Random seed.  Default seed=None which does not specify the random seed.


    """
    import random




    if isinstance(markevery, int):
        if random_start:
            if not seed is None:
                random.seed(seed)
            [apply_dict_to_object(line, d)
            for line, d in
                zip(lines,[{'markevery': (random.randint(0, markevery),
                                          markevery)} for v in lines])]
        else:
            [apply_dict_to_object(line, d)
            for line, d in zip(lines,[{'markevery': markevery} for
            v in lines])]
    elif isinstance(markevery, float):

        try:
            from matplotlib.lines import _mark_every_path
            # the above import should fail for matplotlib <1.4.
            # However, since it was my addition to matplotlib I may have hardwired
            # all the markevery code it in to my own matplotlib.lines file.

            if random_start:
                if not seed is None:
                    random.seed(seed)
                [apply_dict_to_object(line, d)
                for line, d in
                    zip(lines,[{'markevery': (random.random()*markevery,
                                              markevery)} for v in lines])]
            else:
                [apply_dict_to_object(line, d)
                    for line, d in zip(lines,[{'markevery': markevery} for
                    v in lines])]
        except ImportError:
            warnings.warn('markevery=float not available, markevery ignored')

    else:
        #straight application of markevery
        [apply_dict_to_object(line, d)
            for line, d in zip(lines,[{'markevery': markevery} for
            v in lines])]






def plot_vs_depth(x, z, line_labels=None, H = 1.0, RLzero=None,
                   prop_dict={}):
    """Plot z vs x for various t values

    Originally used for plotting things like excess pore pressure vs depth


    ::

        --------------------> value
        |.*
        | .  *
        |  .    *
        |   .     *
        |  .    *
        | .  *
        v
        depth


    Parameters
    ----------
    x :  one or two dimensional ndarray
        y values to plot.  Basically plt.plot(t, y) will be used
    z : one d array of float
        Depth values.
    line_labels : list of string, optional
        Label for each line in y.  Default line_labels=None, i.e. no
        line labels.
    H : float, optional
        Height of soil profile.  Default H=1.0.  Used to transform
        normalised depth to actual depth.
    RLzero : float, optional
        Reduced level of the top of the soil layer.  If RLzero is not None
        then all depths (in plots and results) will be transformed to an
        RL by RL = RLzero - z*H.  If RLzero is None (i.e. the default)
        then actual depths will be reported  z*H (i.e. positive numbers).
    prop_dict : dict of dict, optional
        Dictionary containing certain properties used to set various plot
        options.

        ==================  ============================================
        prop_dict option    description
        ==================  ============================================
        fig_prop            dict of prop to pass to plt.figure.
                            defaults include:
                            figsize=(7.05, 4.4)
        styles              List of dict.  Each dict is for one line.
                            Each dict contains kwargs for plt.plot
                            See
                            MarkersDashesColors
                            defaults give black and white markersize 5
        xlabel              x-axis label. Default = 'x'.
        ylabel              y-axis label. Default = 'Depth, z' or 'RL'.
                            depending on RLzero.
        has_legend          True or False. default is True
        legend_prop         dict of prop to pass to ax.legend
                            defaults include:
                            title='Depth interval'
                            fontsize=9
        ==================  ============================================

    Returns
    -------
    fig : matplolib.Figure
        Figure with plots.

    """

    fig_prop = copy_dict({'figsize':(18/2.54, 18/1.61/2.54)},
                          prop_dict.get('fig_prop', {}))

#    fig_prop = prop_dict.get('fig_prop', {'figsize':(18/2.54, 18/1.61/2.54)})

    legend_prop = copy_dict({'title': 'time:', 'fontsize': 9},
                            prop_dict.get('legend_prop', {}))
#    legend_prop = prop_dict.get('legend_prop',
#                               {'title': 'time:', 'fontsize': 9})

    styles = prop_dict.get('styles', None)
    if styles is None:
        mcd = MarkersDashesColors(
            #color = 'black',
            markersize= 7)
        mcd.construct_styles(markers = list(range(32)), dashes=[0],
                             marker_colors=None, line_colors=None)


        styles = itertools.cycle(mcd.styles)
    else:
        styles = itertools.cycle(styles)



    z = transformations.depth_to_reduced_level(z, H, RLzero)

    fig = plt.figure(**fig_prop)
    plt.plot(x, z)

    xlabel = prop_dict.get('xlabel', 'x')
    plt.xlabel(xlabel)

    if RLzero is None:
        plt.gca().invert_yaxis()
        ylabel = prop_dict.get('ylabel', 'Depth, z')
    else:
        ylabel = prop_dict.get('ylabel', 'RL')

    plt.ylabel(ylabel)

    #apply style to each line
    [apply_dict_to_object(line, d)
        for line, d in zip(fig.gca().get_lines(), styles)]

    #apply markevery to each line
    apply_markevery_to_sequence_of_lines(fig.gca().get_lines(),
                                         markevery=0.1,
                                         random_start=True, seed=1)
#    try:
#        from matplotlib.lines import _mark_every_path
#        # the above import should fail for matplotlib <1.4.
#        # However, since it was my addition to matplotlib I may have hardwired
#        # all the markevery code it in to my own matplotlib.lines file.
#        random.seed(1)
#        [apply_dict_to_object(line, d)
#            for line, d in
#                zip(fig.gca().get_lines(),
#                    [{'markevery': (random.random()* 0.1, 0.1)} for v in x])]
#    except ImportError:
#        pass

    #apply label to each line
    #line_labels = [{'label': '{:.3g}'.format(v)} for v in t]

    if (not line_labels is None):
        labels = [{'label': v} for v in line_labels]
        [apply_dict_to_object(line, d)
            for line, d in zip(fig.gca().get_lines(), labels)]
        has_legend = prop_dict.get('has_legend', True)
    else:
        has_legend=False

#    [apply_dict_to_object(line, d)
#        for line, d in zip(fig.gca().get_lines(), line_labels)]
#
#    has_legend = prop_dict.get('has_legend', True)

    if has_legend:
        leg = fig.gca().legend(**legend_prop)
        leg.draggable(True)
        plt.setp(leg.get_title(),fontsize=legend_prop['fontsize'])
    return fig



if __name__ == '__main__':
    import nose
    nose.runmodule(argv=['nose', '--verbosity=3', '--with-doctest'])
#    nose.runmodule(argv=['nose', '--verbosity=3'])


#    a = MarkersDashesColors()
#    a.color=(0.5, 0, 0)
#    a.default_marker={       'markersize':5,
#                             'markeredgecolor': a.color,
#                             'markeredgewidth':1,
#                             'markerfacecolor': a.color,
#                             'alpha':0.9,
#                             'color': a.color
#                             }
#
#    a.markers=[{'marker': 'o', 'markerfacecolor': 'none'},
#               {'marker': 's'},
#               {'marker': '^'},]
#    a.colors=[(0, 0.5, 0), (0, 0, 0.5)]
#
#    a.dashes=[(None, None), [4, 4]]
#
#    a.merge_default_markers()
#
#    a.construct_styles()
#    a.demo_options()



#    import doctest
#    doctest.testmod()
#    a=MarkersDashesColors()
#    a.demo_options()
#    a.construct_styles()
#    a.construct_styles(markers=[0,5,6,2])
#    a.construct_styles(markers=[0,5,6,2], dashes=[0,3])
#    a.construct_styles(markers=[0,5,6,2], dashes=[0,3], marker_colors=[0,1], line_colors=[2,3])
#    a.demo_styles()


    #plot_data_in_grid(None,[(1,2),(4,5)],[(3,5)])

    #flat = [x for sublist in nested for x in sublist] #http://stackoverflow.com/a/2962856/2530083
#    if 1:
#        pleasing_defaults()
#        fig=plt.figure()
#        x = np.linspace(-np.pi,np.pi,100)
#        d2 = np.linspace(0,1,4)
#        d3 = np.linspace(0,1,2)
#        label1= ['{0:.3g}'.format(i) for i in d2]
#        y1 = np.sin(x)
#        y2 = 1000*np.cos(x[:,np.newaxis]-d2)
#        y3 = 1e-3*np.sin(x[:,np.newaxis]-d3)
#
#
#        data= [[[x,y2]],[[2*x, y1, dict(plot_type='scatter')]], [[1.5*x,y3]]]
#        y_axis_labels=['0','1', '2']
#        x_axis_labels=['Time', None, None]
#
#        #gs = gridspec.GridSpec(shape, hspace=0.08, wspace=0.1)
#        shape=(3,3)
#        gs = gridspec.GridSpec(*shape)
#        transpose = True
#        index_steps=(1,-1)
#        sharey=None
#        sharex=[None,0,None]
#
#        #plot_type=['plot','plot','scatter','plot']
#        gs_index = row_major_order_reverse_map(shape=shape,index_steps=index_steps, transpose=transpose)
#        gs_index = [np.s_[:2,:2],2,8]
#        #gs_index=[1,2,3,0]
#        ax = plot_data_in_grid(fig, data=data, gs=gs,
#                              gs_index=gs_index,
#                              sharex=sharex, sharey=sharey)
#
#
#        styles = MarkersDashesColors()()
#
#
#        [apply_dict_to_object(line, d) for line,d in zip(ax[0].get_lines(), styles)]
#
#
#
#
#
#
#        #apply ylabels to each axis
#        [plt.setp(ax[i], ylabel=label)
#            for i, label in enumerate(y_axis_labels) if not label is None]
#        #apply xlabels to each axis
#        [plt.setp(ax[i], xlabel=label)
#            for i,label in enumerate(x_axis_labels) if not label is None]
#        # turn x tick labels on or off
#        [plt.setp(ax[i].get_xticklabels(), visible=value)
#            for i, value in enumerate([True,False,False]) if not value is None]
#        #gs.tight_layout(fig)
#
#        fig.tight_layout()
#
##Note: axes.flat
#
##        [fig.axes[i]._shared_x_axes.join(fig.axes[i], value) for
##            i,value in enumerate(sharex) if not value is None]
#
#
#        [print(sorted(map(tuple, fig.axes[i]._shared_x_axes))) for
#            i,value in enumerate(sharex) if not value is None]
#        #print(sorted(map(tuple, fig.axes[i]._shared_x_axes)))
#
#        #make the joins
#        [fig.axes[i]._shared_x_axes.join(fig.axes[i], value) for
#            i,value in enumerate(sharex) if not value is None]
#
#        [print(sorted(map(tuple, fig.axes[i]._shared_x_axes))) for
#            i,value in enumerate(sharex) if not value is None]
#        #print(sorted(map(tuple, fig.axes[i]._shared_x_axes)))
##        print([fig.axes[i] in fig.axes[i]._shared_x_axes for
##            i,value in enumerate(sharex) if not value is None]            )
##
#        [fig.axes[i].apply_aspect() for
#            i,value in enumerate(sharex) if not value is None]
#        plt.Axes.get_shared_x_axes()
#        matplot
#        self._shared_x_axes.join(self, sharex)

#        print(plt.getp(fig.axes[i], 'sharex'))
#        [plt.setp(fig.axes[i], sharex=value)
#            for i, value in enumerate(sharex) if not value is None]

#        iterable_method_call(fig.axes, 'set_ylabel', *y_axis_labels)
#        iterable_method_call(fig.axes, 'set_xlabel', *x_axis_labels)
#        iterable_method_call(fig.axes, 'set_xlabel', *x_axis_labels)
#        xylabel_subplots(fig, y_axis_labels,x_axis_labels)

#        plt.show()
#    if 0:
#        x = np.linspace(-np.pi,np.pi,100)
#        d = np.linspace(0,1,4)
#
#        label1= ['{0:.3g}'.format(i) for i in d]
#        y1 = np.sin(x)
#        y2 = np.cos(x[:,np.newaxis]+d)
#        y3 = np.sin(x[:,np.newaxis]+d)
#
#        a= plot_common_x([[[x,y2]],[[x,y1]],[[x,y3]]],
#
#                  x_axis_label='x', y_axis_labels=['$\sigma$', 'load', None], legend_labels=[label1,['surcharge'],label1],
#                  hspace=0.1, height_ratios=[2,1,1],
#                  plot_type='plot',
#                  kwargs_figure=dict(num=3, figsize=(10,10)))
#
#        plt.show()




#    bbox_args = None#dict(boxstyle="round,pad=0.4", fc="yellow",alpha=0.3)
#    bbox_args2 = dict(boxstyle="round,pad=0.6", fc=None, alpha=0)
#    arrow_args = dict(arrowstyle="->")
#    fig=plt.figure()
#    ax = fig.add_subplot(111)
#    np.random.seed(2)
#    x=np.random.randn(100)
#    y=np.random.randn(100)
#    scatter = ax.scatter(x, y, label='h')
#
#    legend=ax.legend()
#    legend.draggable(True)
#
#    anp = ax.annotate('$\hspace{1}$', xy=(x[0], y[0]),  xycoords='data',
#                   xytext=None,  textcoords=None,
#                   ha="center", va="center",
#                   bbox=bbox_args2,
#                   )
#
#    ant = ax.annotate('Drag me 1', xy=(0.5, 0.5),  xycoords=anp,
#                   xytext=(15,0.5),  textcoords=anp,#'offset points',
#                   ha="left", va="center",
#                   bbox=bbox_args,
#                    arrowprops=dict(
#                                   #patchB=anp.get_bbox_patch(),
#                                   connectionstyle="arc3,rad=0.2",
#                                   **arrow_args)
#                   )
#
#
#    anp.draggable()
#    ant.draggable()
#
#
#    plt.show()