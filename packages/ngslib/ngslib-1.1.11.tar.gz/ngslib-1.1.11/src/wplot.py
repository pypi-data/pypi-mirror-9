#!/usr/bin/python
#Last-modified: 05 Nov 2014 10:25:21 AM

#         Module/Scripts Description
# 
# Copyright (c) 2008 Yunfei Wang <yfwang0405@gmail.com>
# 
# This code is free software; you can redistribute it and/or modify it
# under the terms of the BSD License (see the file COPYING included with
# the distribution).
# 
# @status:  experimental
# @version: 1.0.0
# @author:  Yunfei Wang
# @contact: yfwang0405@gmail.com

# ------------------------------------
# python modules
# ------------------------------------

import sys
from pylab import *
import numpy
import itertools 
from matplotlib.backends.backend_pdf import PdfPages

# ------------------------------------
# constants
# ------------------------------------

colors_dict = {
    'automatic'              : '#add8e6',     # 173, 216, 230
    'aliceblue'              : '#f0f8ff',     # 240, 248, 255
    'antiquewhite'           : '#faebd7',     # 250, 235, 215
    'aqua'                   : '#00ffff',     #   0, 255, 255
    'aquamarine'             : '#7fffd4',     # 127, 255, 212
    'azure'                  : '#f0ffff',     # 240, 255, 255
    'beige'                  : '#f5f5dc',     # 245, 245, 220
    'bisque'                 : '#ffe4c4',     # 255, 228, 196
    'black'                  : '#000000',     #   0,   0,   0
    'blanchedalmond'         : '#ffebcd',     # 255, 235, 205
    'blue'                   : '#0000ff',     #   0,   0, 255
    'blueviolet'             : '#8a2be2',     # 138,  43, 226
    'brown'                  : '#a52a2a',     # 165,  42,  42
    'burlywood'              : '#deb887',     # 222, 184, 135
    'cadetblue'              : '#5f9ea0',     #  95, 158, 160
    'chartreuse'             : '#7fff00',     # 127, 255,   0
    'chocolate'              : '#d2691e',     # 210, 105,  30
    'coral'                  : '#ff7f50',     # 255, 127,  80
    'cornflowerblue'         : '#6495ed',     # 100, 149, 237
    'cornsilk'               : '#fff8dc',     # 255, 248, 220
    'crimson'                : '#dc143c',     # 220,  20,  60
    'cyan'                   : '#00ffff',     #   0, 255, 255
    'darkblue'               : '#00008b',     #   0,   0, 139
    'darkcyan'               : '#008b8b',     #   0, 139, 139
    'darkgoldenrod'          : '#b8860b',     # 184, 134,  11
    'darkgray'               : '#a9a9a9',     # 169, 169, 169
    'darkgreen'              : '#006400',     #   0, 100,   0
    'darkgrey'               : '#a9a9a9',     # 169, 169, 169
    'darkkhaki'              : '#bdb76b',     # 189, 183, 107
    'darkmagenta'            : '#8b008b',     # 139,   0, 139
    'darkolivegreen'         : '#556b2f',     #  85, 107,  47
    'darkorange'             : '#ff8c00',     # 255, 140,   0
    'darkorchid'             : '#9932cc',     # 153,  50, 204
    'darkred'                : '#8b0000',     # 139,   0,   0
    'darksalmon'             : '#e9967a',     # 233, 150, 122
    'darkseagreen'           : '#8fbc8f',     # 143, 188, 143
    'darkslateblue'          : '#483d8b',     #  72,  61, 139
    'darkslategray'          : '#2f4f4f',     #  47,  79,  79
    'darkslategrey'          : '#2f4f4f',     #  47,  79,  79
    'darkturquoise'          : '#00ced1',     #   0, 206, 209
    'darkviolet'             : '#9400d3',     # 148,   0, 211
    'deeppink'               : '#ff1493',     # 255,  20, 147
    'deepskyblue'            : '#00bfff',     #   0, 191, 255
    'dimgray'                : '#696969',     # 105, 105, 105
    'dimgrey'                : '#696969',     # 105, 105, 105
    'dodgerblue'             : '#1e90ff',     #  30, 144, 255
    'firebrick'              : '#b22222',     # 178,  34,  34
    'floralwhite'            : '#fffaf0',     # 255, 250, 240
    'forestgreen'            : '#228b22',     #  34, 139,  34
    'fuchsia'                : '#ff00ff',     # 255,   0, 255
    'gainsboro'              : '#dcdcdc',     # 220, 220, 220
    'ghostwhite'             : '#f8f8ff',     # 248, 248, 255
    'gold'                   : '#ffd700',     # 255, 215,   0
    'goldenrod'              : '#daa520',     # 218, 165,  32
    'gray'                   : '#808080',     # 128, 128, 128
    'green'                  : '#008000',     #   0, 128,   0
    'greenyellow'            : '#adff2f',     # 173, 255,  47
    'grey'                   : '#808080',     # 128, 128, 128
    'honeydew'               : '#f0fff0',     # 240, 255, 240
    'hotpink'                : '#ff69b4',     # 255, 105, 180
    'indianred'              : '#cd5c5c',     # 205,  92,  92
    'indigo'                 : '#4b0082',     #  75,   0, 130
    'ivory'                  : '#fffff0',     # 255, 255, 240
    'khaki'                  : '#f0e68c',     # 240, 230, 140
    'lavender'               : '#e6e6fa',     # 230, 230, 250
    'lavenderblush'          : '#fff0f5',     # 255, 240, 245
    'lawngreen'              : '#7cfc00',     # 124, 252,   0
    'lemonchiffon'           : '#fffacd',     # 255, 250, 205
    'lightblue'              : '#add8e6',     # 173, 216, 230
    'lightcoral'             : '#f08080',     # 240, 128, 128
    'lightcyan'              : '#e0ffff',     # 224, 255, 255
    'lightgoldenrodyellow'   : '#fafad2',     # 250, 250, 210
    'lightgray'              : '#d3d3d3',     # 211, 211, 211
    'lightgreen'             : '#90ee90',     # 144, 238, 144
    'lightgrey'              : '#d3d3d3',     # 211, 211, 211
    'lightpink'              : '#ffb6c1',     # 255, 182, 193
    'lightsalmon'            : '#ffa07a',     # 255, 160, 122
    'lightseagreen'          : '#20b2aa',     #  32, 178, 170
    'lightskyblue'           : '#87cefa',     # 135, 206, 250
    'lightslategray'         : '#778899',     # 119, 136, 153
    'lightslategrey'         : '#778899',     # 119, 136, 153
    'lightsteelblue'         : '#b0c4de',     # 176, 196, 222
    'lightyellow'            : '#ffffe0',     # 255, 255, 224
    'lime'                   : '#00ff00',     #   0, 255,   0
    'limegreen'              : '#32cd32',     #  50, 205,  50
    'linen'                  : '#faf0e6',     # 250, 240, 230
    'magenta'                : '#ff00ff',     # 255,   0, 255
    'maroon'                 : '#800000',     # 128,   0,   0
    'mediumaquamarine'       : '#66cdaa',     # 102, 205, 170
    'mediumblue'             : '#0000cd',     #   0,   0, 205
    'mediumorchid'           : '#ba55d3',     # 186,  85, 211
    'mediumpurple'           : '#9370db',     # 147, 112, 219
    'mediumseagreen'         : '#3cb371',     #  60, 179, 113
    'mediumslateblue'        : '#7b68ee',     # 123, 104, 238
    'mediumspringgreen'      : '#00fa9a',     #   0, 250, 154
    'mediumturquoise'        : '#48d1cc',     #  72, 209, 204
    'mediumvioletred'        : '#c71585',     # 199,  21, 133
    'midnightblue'           : '#191970',     #  25,  25, 112
    'mintcream'              : '#f5fffa',     # 245, 255, 250
    'mistyrose'              : '#ffe4e1',     # 255, 228, 225
    'moccasin'               : '#ffe4b5',     # 255, 228, 181
    'navajowhite'            : '#ffdead',     # 255, 222, 173
    'navy'                   : '#000080',     #   0,   0, 128
    'oldlace'                : '#fdf5e6',     # 253, 245, 230
    'olive'                  : '#808000',     # 128, 128,   0
    'olivedrab'              : '#6b8e23',     # 107, 142,  35
    'orange'                 : '#ffa500',     # 255, 165,   0
    'orangered'              : '#ff4500',     # 255,  69,   0
    'orchid'                 : '#da70d6',     # 218, 112, 214
    'palegoldenrod'          : '#eee8aa',     # 238, 232, 170
    'palegreen'              : '#98fb98',     # 152, 251, 152
    'paleturquoise'          : '#afeeee',     # 175, 238, 238
    'palevioletred'          : '#db7093',     # 219, 112, 147
    'papayawhip'             : '#ffefd5',     # 255, 239, 213
    'peachpuff'              : '#ffdab9',     # 255, 218, 185
    'peru'                   : '#cd853f',     # 205, 133,  63
    'pink'                   : '#ffc0cb',     # 255, 192, 203
    'plum'                   : '#dda0dd',     # 221, 160, 221
    'powderblue'             : '#b0e0e6',     # 176, 224, 230
    'purple'                 : '#800080',     # 128,   0, 128
    'red'                    : '#ff0000',     # 255,   0,   0
    'rosybrown'              : '#bc8f8f',     # 188, 143, 143
    'royalblue'              : '#4169e1',     #  65, 105, 225
    'saddlebrown'            : '#8b4513',     # 139,  69,  19
    'salmon'                 : '#fa8072',     # 250, 128, 114
    'sandybrown'             : '#f4a460',     # 244, 164,  96
    'seagreen'               : '#2e8b57',     #  46, 139,  87
    'seashell'               : '#fff5ee',     # 255, 245, 238
    'sienna'                 : '#a0522d',     # 160,  82,  45
    'silver'                 : '#c0c0c0',     # 192, 192, 192
    'skyblue'                : '#87ceeb',     # 135, 206, 235
    'slateblue'              : '#6a5acd',     # 106,  90, 205
    'slategray'              : '#708090',     # 112, 128, 144
    'slategrey'              : '#708090',     # 112, 128, 144
    'snow'                   : '#fffafa',     # 255, 250, 250
    'springgreen'            : '#00ff7f',     #   0, 255, 127
    'steelblue'              : '#4682b4',     #  70, 130, 180
    'tan'                    : '#d2b48c',     # 210, 180, 140
    'teal'                   : '#008080',     #   0, 128, 128
    'thistle'                : '#d8bfd8',     # 216, 191, 216
    'tomato'                 : '#ff6347',     # 255,  99,  71
    'turquoise'              : '#40e0d0',     #  64, 224, 208
    'violet'                 : '#ee82ee',     # 238, 130, 238
    'wheat'                  : '#f5deb3',     # 245, 222, 179
    'white'                  : '#ffffff',     # 255, 255, 255
    'whitesmoke'             : '#f5f5f5',     # 245, 245, 245
    'yellow'                 : '#ffff00',     # 255, 255,   0
    'yellowgreen'            : '#9acd32'      # 154, 205,  50
}

# ------------------------------------
# Misc functions
# ------------------------------------

# ------------------------------------
# Classes
# ------------------------------------

class plot(object):
    ''' Functions used to plot. '''
    def set_font():
        ''' Set font to Arial '''
        # font size for figures
        rcParams.update({'font.size': 16})
        # Arial font
        rc('font',**{'family':'sans-serif','sans-serif':['Arial']})
    set_font=staticmethod(set_font)
    def clean_axes(ax):
        '''
        Remove ticks, tick labels, and frame from axis
        helper for cleaning up axes by removing ticks, tick labels, frame, etc.
        '''
        ax.get_xaxis().set_ticks([])
        ax.get_yaxis().set_ticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)
    def set_box_colors(bp,col,fcol):
        '''
        Set colors for boxplot. 
        Note the boxplot should generated with parameter: patch_artist=True
        '''
        setp(bp['boxes'][0], color=col,linewidth=1,facecolor = fcol)
        setp(bp['caps'][0], color=col)
        setp(bp['caps'][1], color=col)
        setp(bp['whiskers'][0], color=col)
        setp(bp['whiskers'][1], color=col)
        setp(bp['fliers'][0], color=col)
        setp(bp['fliers'][1], color=col)
        setp(bp['medians'][0], color=col)
        return
    set_box_colors=staticmethod(set_box_colors)
    def set_group_box_colors(bp,cols,fcols,mcol='black'):
        '''
        Set colors in group for boxplot.
        Note the boxplot should generated with parameter: patch_artist=True
        Parameters:
            bp:    boxplot object
            cols:  colors for lines
            fcols: colors to fill
            mcol:  color for median line
        Usage:
            bp = boxplot(data,"","",patch_artist=True)
            set_group_box_colors(bp,[col1,col2,...],[fcol1,fcol2,...],'black')
        Note:
            1. set "patch_artist=True" in boxplot
            2. cols and fcols should be in pair.
        '''
        nc = len(cols) # number of colors
        nb = len(bp['boxes']) # number of boxes

        for i in range(nb): # for every box
            j = i%nc # jth in group
            setp(bp['boxes'][i], color=cols[j],linewidth=1,facecolor = fcols[j])
            setp(bp['medians'][i], color=mcol)
            for item in ['caps','whiskers','fliers']:
                setp(bp[item][2*i], color=cols[j])
                setp(bp[item][2*i+1], color=cols[j])            
        return
    set_group_box_colors=staticmethod(set_group_box_colors)
    def set_axes_frame(ax,bottom=True,left=True,top=True,right=True):
        '''
        Set axis frames visible or not.
        Parameters:
            ax: matplotlib.axes.AxesSubplot
                ax = gca() to get the current axes object.
            bottom: bool
                True if visible, otherwise invisible.
            left: bool
                True if visible, otherwise invisible.
            top: bool
                True if visible, otherwise invisible.
            right: bool
                True if visible, otherwise invisible.
        '''
        ax.spines['top'].set_visible(top)
        ax.spines['bottom'].set_visible(bottom)
        ax.spines['left'].set_visible(left)
        ax.spines['right'].set_visible(right)
    set_axes_frame=staticmethod(set_axes_frame)
    def draw_color_panel(fname="ColorPanel.pdf"):
        ''' Draw color panel. '''
        pp = PdfPages('ColorPanel.pdf')
        figure(figsize=(8,37))
        #plot([1,3,2])
        xlim(0,8)
        ylim(0,37)
        xticks([])
        yticks([])
        ax=gca()
        for i,col in enumerate(colors_dict):
            idx = i%4*2
            idy = i/4
            ax.add_patch(Rectangle((idx,idy), 2, 1,facecolor=colors_dict[col]))
            text(idx+1,idy+0.5,col,horizontalalignment='center',verticalalignment='center')
        pp.savefig()
        pp.close()
    draw_color_panel=staticmethod(draw_color_panel)
    def dendrogram(df,orientation='top',no_plot=True,color_threshold=False):
        '''
        Dendrogram.
        Parameters:
            df: pandas.DataFrame
                data
            orientation: string
                root orientation: 'top','bottom','left','right'
            no_plot: bool
                plot the dendrogram if True
            color_threshold: bool
                color the dendrogram if True

        '''
        # calculate pairwise distances for rows
        pairwise_dists = distance.squareform(distance.pdist(df))
        # cluster
        clusters = sch.linkage(pairwise_dists,method='complete')
        # dendrogram
        # make dendrograms black rather than letting scipy color them
        #sch.set_link_color_palette(['black'])
        #den = sch.dendrogram(clusters,color_threshold=np.inf)
        if color_threshold :
            den = sch.dendrogram(clusters,orientation=orientation,no_plot=no_plot)
        else:
            den = sch.dendrogram(clusters,orientation=orientation,no_plot=no_plot,color_threshold=numpy.inf)
        return den
    dendrogram=staticmethod(dendrogram)

    def custom_axis(ax, left='k', bottom='k', right='none', top='none',lw=.5, size=12, pad=8):
        '''
        Customize axis.
        Parameters:
            ax: axes object
                figure axes object
            left: string
                colors or 'none'
            lw: float
                line width
            size: int
                font size
            pad: int
                pad
        '''
        for c_spine, spine in zip([c_left, c_bottom, c_right, c_top],
                                  ['left', 'bottom', 'right', 'top']):
            if c_spine != 'none':
                ax.spines[spine].set_color(c_spine)
                ax.spines[spine].set_linewidth(lw)
            else:
                ax.spines[spine].set_color('none')
        if (c_bottom == 'none') & (c_top == 'none'): # no bottom and no top
            ax.xaxis.set_ticks_position('none')
        elif (c_bottom != 'none') & (c_top != 'none'): # bottom and top
            ax.tick_params(axis='x', direction='out', width=lw, length=7,
                          color=c_bottom, labelsize=size, pad=pad)
        elif (c_bottom != 'none') & (c_top == 'none'): # bottom but not top
            ax.xaxis.set_ticks_position('bottom')
            ax.tick_params(axis='x', direction='out', width=lw, length=7,
                           color=c_bottom, labelsize=size, pad=pad)
        elif (c_bottom == 'none') & (c_top != 'none'): # no bottom but top
            ax.xaxis.set_ticks_position('top')
            ax.tick_params(axis='x', direction='out', width=lw, length=7,
                           color=c_top, labelsize=size, pad=pad)
        if (c_left == 'none') & (c_right == 'none'): # no left and no right
            ax.yaxis.set_ticks_position('none')
        elif (c_left != 'none') & (c_right != 'none'): # left and right
            ax.tick_params(axis='y', direction='out', width=lw, length=7,
                           color=c_left, labelsize=size, pad=pad)
        elif (c_left != 'none') & (c_right == 'none'): # left but not right
            ax.yaxis.set_ticks_position('left')
            ax.tick_params(axis='y', direction='out', width=lw, length=7,
                           color=c_left, labelsize=size, pad=pad)
        elif (c_left == 'none') & (c_right != 'none'): # no left but right
            ax.yaxis.set_ticks_position('right')
            ax.tick_params(axis='y', direction='out', width=lw, length=7,
                           color=c_right, labelsize=size, pad=pad)
    custom_axis=staticmethod(custom_axis)
    def scatterplot_matrix(data, names, **kwargs):
        """Plots a scatterplot matrix of subplots.  Each row of "data" is plotted
        against other rows, resulting in a nrows by nrows grid of subplots with the
        diagonal subplots labeled with "names".  Additional keyword arguments are
        passed on to matplotlib's "plot" command. Returns the matplotlib figure
        object containg the subplot grid."""
        numvars, numdata = data.shape
        fig, axes = subplots(nrows=numvars, ncols=numvars, figsize=(8,8))
        fig.subplots_adjust(hspace=0.05, wspace=0.05)
    
        for ax in axes.flat:
            # Hide all ticks and labels
            ax.xaxis.set_visible(False)
            ax.yaxis.set_visible(False)
    
            # Set up ticks only on one side for the "edge" subplots...
            if ax.is_first_col():
                ax.yaxis.set_ticks_position('left')
            if ax.is_last_col():
                ax.yaxis.set_ticks_position('right')
            if ax.is_first_row():
                ax.xaxis.set_ticks_position('top')
            if ax.is_last_row():
                ax.xaxis.set_ticks_position('bottom')
    
        # Plot the data.
        for i, j in zip(*numpy.triu_indices_from(axes, k=1)):
            for x, y in [(i,j), (j,i)]:
                axes[x,y].plot(data[x], data[y], **kwargs)
    
        # Label the diagonal subplots...
        for i, label in enumerate(names):
            axes[i,i].annotate(label, (0.5, 0.5), xycoords='axes fraction',
                    ha='center', va='center')
    
        # Turn on the proper x or y axes ticks.
        for i, j in zip(range(numvars), itertools.cycle((-1, 0))):
            axes[j,i].xaxis.set_visible(True)
            axes[i,j].yaxis.set_visible(True)
    
        return fig
    scatterplot_matrix=staticmethod(scatterplot_matrix)


class Utils(object):
    ''' Utilities. '''
    def pdf(fname):
        '''
        Save figure in pdf format.
        Usage:
            pp = pdf('test.pdf')
            # draw figure
            pp.savefig()
            pp.close()
        '''
        return PdfPages(fname) 
    pdf=staticmethod(pdf)

# ------------------------------------
# Main
# ------------------------------------

if __name__=="__main__":
    if len(sys.argv)==1:
        sys.exit("Example:"+sys.argv[0]+" file1 file2... ")

