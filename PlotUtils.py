import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
from pylab import *
import itertools
from sklearn.metrics import confusion_matrix

# Para cambiar el mapa de color por defecto
plt.rcParams["image.cmap"] = "Set2"
# Para cambiar el ciclo de color por defecto en Matplotlib
# plt.rcParams['axes.prop_cycle'] = plt.cycler(color=plt.cm.Set2.colors)
# plt.rcParams["axes.prop_cycle"] =  plt.cycler('color', ['#8C6D31', '#ffdd6b', '#e9e2c9', '#dcae52', '#af7132', '#8C9363', '#637939', '#AD494A', '#E7969C', '#C4CBB9'])
# plt.rcParams["axes.prop_cycle"] =  plt.cycler('color', ['#081d58', '#253494', '#225ea8', '#1d91c0', '#41b6c4', '#7fcdbb', '#c7e9b4', '#edf8b1', '#ffffd9'])
# plt.rcParams["axes.prop_cycle"] =  plt.cycler('color', ['#084081', '#0868ac', '#2b8cbe', '#4eb3d3', '#7bccc4', '#a8ddb5', '#ccebc5', '#e0f3db', '#f7fcf0'])
# plt.rcParams["axes.prop_cycle"] =  plt.cycler('color', ['#67001f', '#b2182b', '#d6604d', '#f4a582', '#fddbc7', '#d1e5f0', '#92c5de', '#4393c3', '#2166ac','#053061'])
# plt.rcParams["axes.prop_cycle"] =  plt.cycler('color', ['#67001f', '#053061', '#b2182b', '#2166ac', '#d6604d', '#4393c3', '#f4a582', '#92c5de', '#fddbc7','#d1e5f0'])
# plt.rcParams["axes.prop_cycle"] =  plt.cycler('color', ['#67001f', '#053061', '#b2182b', '#2166ac', '#d6604d', '#4393c3', '#f4a582', '#92c5de', '#fddbc7','#d1e5f0'][::-1])
# plt.rcParams["axes.prop_cycle"] =  plt.cycler('color', ['#8dd3c7', '#ffffb3', '#bebada', '#fb8072', '#80b1d3', '#fdb462', '#b3de69', '#fccde5', '#d9d9d9','#bc80bd','#ccebc5','#ffed6f'])
# plt.rcParams["axes.prop_cycle"] =  plt.cycler('color', ['#8dd3c7', '#ffffb3', '#bebada', '#fb8072', '#80b1d3', '#fdb462', '#b3de69', '#fccde5', '#d9d9d9','#bc80bd','#ccebc5','#ffed6f'][::-1])

def Set_ColorsIn(cyc=None):
    global clrs
    if cyc:
        clrs = cyc

def donutPlot(data, recipe, title = False,png = False, pdf = False, legend = True, figsize=(18, 9), fontset=False):
    if fontset:
        plt.rc('font', size=fontset)
    fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(aspect="equal"))

    wedges, texts = ax.pie(data, wedgeprops=dict(width=0.25), startangle=-40)

    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    kw = dict(arrowprops=dict(arrowstyle="-"),
              bbox=bbox_props, zorder=0, va="center")

    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1)/2. + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = "angle,angleA=0,angleB={}".format(ang)
        kw["arrowprops"].update({"connectionstyle": connectionstyle})
        if not legend:
            ax.annotate(recipe[i], xy=(x, y), xytext=(1.35*np.sign(x), 1.4*y),
                    horizontalalignment=horizontalalignment, **kw)

    if legend:
        ax.legend(wedges, recipe,
                  title= title,
                  loc="center left",
                  bbox_to_anchor=(1, 0, 0.5, 1))

    if png:
        plt.savefig(png + '.png', transparent=True)
    if pdf:
        plt.savefig(pdf + '.pdf', transparent=True)
    plt.show()

def groupedBarPlot(data, xticks, title,legend=True,axislabels = False,width=0.35,figsize=(25,10), barLabel=False, png = False, pdf = False, colors = None, fsizes = False, axisLim = False, xtick_rot=False, bLconfs = ['%.2f', 14], labRot = 0, barh=False):
    """Width recomendado para 2 barras agrupadas es 0.35, para 3 y 4 es 0.2
       Para usar el barLabel, debe ser una lista de listas por cada tipo,
       aun que sea solo una barra por paso en el eje x deber ser una lista contenida dentro de otra
       Las opciones para fsizes son:
            'font' --> controla el tamaño de los textos por defecto
            'axes' --> tamaño de fuente del titulo y las etiquetas del eje x & y
            'xtick' --> tamaño de fuente de los puntos en el eje x
            'ytick' --> tamaño de fuente en los puntos del eje y
            'legend --> controla el tamaño de fuente de la leyenda
            'figure' --> controla el tamaño de fuente del titulo de la figura
       """
    if fsizes:
        for key,size in fsizes.items():
            if key == 'font':
                plt.rc(key, size=size)
            elif key == 'axes':
                plt.rc(key, titlesize=size)
                plt.rc(key, labelsize=size)
            elif key in ['xtick','ytick']:
                plt.rc(key, labelsize=size)
            elif key == 'legend':
                plt.rc(key, fontsize=size)
            elif key == 'figure':
                plt.rc(key, titlesize=size)
    else:
        plt.rc('font', size=15)

    x = np.arange(len(xticks))
    if colors:
        cl = colors
    else:
        cl = clrs

    if figsize:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig, ax = plt.subplots()

    rects = {}
    if not barh:
        if len(data) == 1:
            ldata = list(data.values())
            keys = list(data.keys())
            rects[keys[0]] = ax.bar(x, ldata[0], width, label=keys[0], color = cl)
        elif len(data) == 2:
            ldata = list(data.values())
            keys = list(data.keys())
            rects[keys[0]] = ax.bar(x + width/2, ldata[0], width, label=keys[0], color = cl[2])
            rects[keys[1]] = ax.bar(x - width/2, ldata[1], width, label=keys[1], color = cl[3])
        elif len(data) == 3:
            ldata = list(data.values())
            keys = list(data.keys())
            rects[keys[0]] = ax.bar(x, ldata[0], width, label=keys[0])
            rects[keys[1]] = ax.bar([i+width for i in x], ldata[1], width, label=keys[1])
            rects[keys[2]] = ax.bar([i+2*width for i in x], ldata[2], width, label=keys[2])
        elif len(data) == 4:
            ldata = list(data.values())
            keys = list(data.keys())
            rects[keys[0]] = ax.bar(x + width/2, ldata[0], width, label=keys[0], color = cl[0])
            rects[keys[1]] = ax.bar(x - width/2, ldata[1], width, label=keys[1], color = cl[1])
            rects[keys[2]] = ax.bar(x + 1.5*width, ldata[2], width, label=keys[2], color = cl[2])
            rects[keys[3]] = ax.bar(x - 1.5*width, ldata[3], width, label=keys[3], color = cl[3])

        # ax.patch.set_facecolor('red')
        ax.patch.set_alpha(0.0)

        if axislabels:
            ax.set_xlabel(axislabels[0])
            ax.set_ylabel(axislabels[1])

        ax.set_title(title)
        if len(data) == 3:
            ax.set_xticks(x+width)
        else:
            ax.set_xticks(x, labels = xticks)
        if xtick_rot:
            ax.set_xticklabels(xticks, rotation = xtick_rot)
        else:
            ax.set_xticklabels(xticks)
    else:
        if len(data) == 1:
            ldata = list(data.values())
            keys = list(data.keys())
            rects[keys[0]] = ax.barh(x, ldata[0], width, label=keys[0], color = cl)
        elif len(data) == 2:
            ldata = list(data.values())
            keys = list(data.keys())
            rects[keys[0]] = ax.barh(x + width/2, ldata[0], width, label=keys[0], color = cl[2])
            rects[keys[1]] = ax.barh(x - width/2, ldata[1], width, label=keys[1], color = cl[3])
        elif len(data) == 3:
            ldata = list(data.values())
            keys = list(data.keys())
            rects[keys[0]] = ax.barh(x, ldata[0], width, label=keys[0])
            rects[keys[1]] = ax.barh([i+width for i in x], ldata[1], width, label=keys[1])
            rects[keys[2]] = ax.barh([i+2*width for i in x], ldata[2], width, label=keys[2])
        elif len(data) == 4:
            ldata = list(data.values())
            keys = list(data.keys())
            rects[keys[0]] = ax.barh(x + width/2, ldata[0], width, label=keys[0], color = cl[0])
            rects[keys[1]] = ax.barh(x - width/2, ldata[1], width, label=keys[1], color = cl[1])
            rects[keys[2]] = ax.barh(x + 1.5*width, ldata[2], width, label=keys[2], color = cl[2])
            rects[keys[3]] = ax.barh(x - 1.5*width, ldata[3], width, label=keys[3], color = cl[3])

        # ax.patch.set_facecolor('red')
        ax.patch.set_alpha(0.0)

        if axislabels:
            ax.set_xlabel(axislabels[1])
            ax.set_ylabel(axislabels[0])

        ax.set_title(title)
        if len(data) == 3:
            ax.set_yticks(x+width)
        else:
            ax.set_yticks(x, labels = xticks)
        if xtick_rot:
            ax.set_yticklabels(xticks, rotation = xtick_rot)
        else:
            ax.set_yticklabels(xticks)

    if legend:
        ax.legend(prop={"size":30})

    if barLabel:
        try:
            for j,i in enumerate(rects.values()):
                ax.bar_label(i, padding=3, labels=[barLabel[0][:].format(ldata[j][r], barLabel[j+1][r]) for r in range(len(ldata[0]))], rotation = labRot)
        except:
            for j,i in enumerate(rects.values()):
                ax.bar_label(i, padding=3, labels=['{}\n{:.2f}%'.format(ldata[j][r], barLabel[j][r]) for r in range(len(ldata[0]))], rotation = labRot)
    else:
        for i in rects.values():
            ax.bar_label(i, padding=3, fmt = bLconfs[0], fontsize = bLconfs[1], rotation = labRot)

    fig.tight_layout()

    if axisLim:
        for key,values in axisLim.items():
            if key == 'xlim':
                plt.xlim(values[0], values[1])
            elif key == 'ylim':
                plt.ylim(values[0], values[1])

    if png:
        plt.savefig(png + '.png', transparent=True)
    if pdf:
        plt.savefig(pdf + '.pdf', transparent=True)

    plt.show()

LW = 0.3

def polar2xy(r, theta):
    return np.array([r*np.cos(theta), r*np.sin(theta)])

def hex2rgb(c):
    return tuple(int(c[i:i+2], 16)/256.0 for i in (1, 3 ,5))

def IdeogramArc(start=0, end=60, radius=1.0, width=0.2, ax=None, color=(1,0,0)):
    # start, end should be in [0, 360)
    if start > end:
        start, end = end, start
    start *= np.pi/180.
    end *= np.pi/180.
    # optimal distance to the control points
    # https://stackoverflow.com/questions/1734745/how-to-create-circle-with-b%C3%A9zier-curves
    opt = 4./3. * np.tan((end-start)/ 4.) * radius
    inner = radius*(1-width)
    verts = [
        polar2xy(radius, start),
        polar2xy(radius, start) + polar2xy(opt, start+0.5*np.pi),
        polar2xy(radius, end) + polar2xy(opt, end-0.5*np.pi),
        polar2xy(radius, end),
        polar2xy(inner, end),
        polar2xy(inner, end) + polar2xy(opt*(1-width), end-0.5*np.pi),
        polar2xy(inner, start) + polar2xy(opt*(1-width), start+0.5*np.pi),
        polar2xy(inner, start),
        polar2xy(radius, start),
        ]

    codes = [Path.MOVETO,
             Path.CURVE4,
             Path.CURVE4,
             Path.CURVE4,
             Path.LINETO,
             Path.CURVE4,
             Path.CURVE4,
             Path.CURVE4,
             Path.CLOSEPOLY,
             ]

    if ax == None:
        return verts, codes
    else:
        path = Path(verts, codes)
        patch = patches.PathPatch(path, facecolor=color+(0.5,), edgecolor=color+(0.4,), lw=LW)
        ax.add_patch(patch)


def ChordArc(start1=0, end1=60, start2=180, end2=240, radius=1.0, chordwidth=0.7, ax=None, color=(1,0,0)):
    # start, end should be in [0, 360)
    if start1 > end1:
        start1, end1 = end1, start1
    if start2 > end2:
        start2, end2 = end2, start2
    start1 *= np.pi/180.
    end1 *= np.pi/180.
    start2 *= np.pi/180.
    end2 *= np.pi/180.
    opt1 = 4./3. * np.tan((end1-start1)/ 4.) * radius
    opt2 = 4./3. * np.tan((end2-start2)/ 4.) * radius
    rchord = radius * (1-chordwidth)
    verts = [
        polar2xy(radius, start1),
        polar2xy(radius, start1) + polar2xy(opt1, start1+0.5*np.pi),
        polar2xy(radius, end1) + polar2xy(opt1, end1-0.5*np.pi),
        polar2xy(radius, end1),
        polar2xy(rchord, end1),
        polar2xy(rchord, start2),
        polar2xy(radius, start2),
        polar2xy(radius, start2) + polar2xy(opt2, start2+0.5*np.pi),
        polar2xy(radius, end2) + polar2xy(opt2, end2-0.5*np.pi),
        polar2xy(radius, end2),
        polar2xy(rchord, end2),
        polar2xy(rchord, start1),
        polar2xy(radius, start1),
        ]

    codes = [Path.MOVETO,
             Path.CURVE4,
             Path.CURVE4,
             Path.CURVE4,
             Path.CURVE4,
             Path.CURVE4,
             Path.CURVE4,
             Path.CURVE4,
             Path.CURVE4,
             Path.CURVE4,
             Path.CURVE4,
             Path.CURVE4,
             Path.CURVE4,
             ]

    if ax == None:
        return verts, codes
    else:
        path = Path(verts, codes)
        patch = patches.PathPatch(path, facecolor=color+(0.5,), edgecolor=color+(0.4,), lw=LW)
        ax.add_patch(patch)

def selfChordArc(start=0, end=60, radius=1.0, chordwidth=0.7, ax=None, color=(1,0,0)):
    # start, end should be in [0, 360)
    if start > end:
        start, end = end, start
    start *= np.pi/180.
    end *= np.pi/180.
    opt = 4./3. * np.tan((end-start)/ 4.) * radius
    rchord = radius * (1-chordwidth)
    verts = [
        polar2xy(radius, start),
        polar2xy(radius, start) + polar2xy(opt, start+0.5*np.pi),
        polar2xy(radius, end) + polar2xy(opt, end-0.5*np.pi),
        polar2xy(radius, end),
        polar2xy(rchord, end),
        polar2xy(rchord, start),
        polar2xy(radius, start),
        ]

    codes = [Path.MOVETO,
             Path.CURVE4,
             Path.CURVE4,
             Path.CURVE4,
             Path.CURVE4,
             Path.CURVE4,
             Path.CURVE4,
             ]

    if ax == None:
        return verts, codes
    else:
        path = Path(verts, codes)
        patch = patches.PathPatch(path, facecolor=color+(0.5,), edgecolor=color+(0.4,), lw=LW)
        ax.add_patch(patch)

def chordDiagram(X, ax, colors=None, width=0.1, pad=2, chordwidth=0.7, png = False, pdf = False):
    """Plot a chord diagram
    Parameters
    ----------
    X :
        flux data, X[i, j] is the flux from i to j
    ax :
        matplotlib `axes` to show the plot
    colors : optional
        user defined colors in rgb format. Use function hex2rgb() to convert hex color to rgb color. Default: d3.js category10
    width : optional
        width/thickness of the ideogram arc
    pad : optional
        gap pad between two neighboring ideogram arcs, unit: degree, default: 2 degree
    chordwidth : optional
        position of the control points for the chords, controlling the shape of the chords
    """
    # X[i, j]:  i -> j
    x = X.sum(axis = 1) # sum over rows
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)

    if colors is None:
    # use d3.js category10 https://github.com/d3/d3-3.x-api-reference/blob/master/Ordinal-Scales.md#category10
        colors = ['#67001f', '#053061', '#b2182b', '#2166ac', '#d6604d', '#4393c3', '#f4a582', '#92c5de', '#fddbc7','#d1e5f0'][::-1]
        if len(x) > 10:
            print('x is too large! Use x smaller than 10')
        colors = [hex2rgb(colors[i]) for i in range(len(x))]

    # find position for each start and end
    y = x/np.sum(x).astype(float) * (360 - pad*len(x))

    pos = {}
    arc = []
    nodePos = []
    start = 0
    for i in range(len(x)):
        end = start + y[i]
        arc.append((start, end))
        angle = 0.5*(start+end)
        #print(start, end, angle)
        if -30 <= angle <= 210:
            angle -= 90
        else:
            angle -= 270
        nodePos.append(tuple(polar2xy(1.1, 0.5*(start+end)*np.pi/180.)) + (angle,))
        z = (X[i, :]/x[i].astype(float)) * (end - start)
        ids = np.argsort(z)
        z0 = start
        for j in ids:
            pos[(i, j)] = (z0, z0+z[j])
            z0 += z[j]
        start = end + pad

    for i in range(len(x)):
        start, end = arc[i]
        IdeogramArc(start=start, end=end, radius=1.0, ax=ax, color=colors[i], width=width)
        start, end = pos[(i,i)]
        selfChordArc(start, end, radius=1.-width, color=colors[i], chordwidth=chordwidth*0.7, ax=ax)
        for j in range(i):
            color = colors[i]
            if X[i, j] > X[j, i]:
                color = colors[j]
            start1, end1 = pos[(i,j)]
            start2, end2 = pos[(j,i)]
            ChordArc(start1, end1, start2, end2,
                     radius=1.-width, color=colors[i], chordwidth=chordwidth, ax=ax)

    if png:
        plt.savefig(png + '.png', transparent=True)
    if pdf:
        plt.savefig(pdf + '.pdf', transparent=True)
    #print(nodePos)
    return nodePos

def plot_confusion_matrix(cm, classes, normalize=False,colors = None,tit = False, axisLabels=False,fsizes = False, xtickRot = 45, png = False, pdf = False):
    if fsizes:
        for key,size in fsizes.items():
            if key == 'font':
                plt.rc(key, size=size)
            elif key == 'axes':
                plt.rc(key, titlesize=size)
                plt.rc(key, labelsize=size)
            elif key in ['xtick','ytick']:
                plt.rc(key, labelsize=size)
            elif key == 'legend':
                plt.rc(key, fontsize=size)
            elif key == 'figure':
                plt.rc(key, titlesize=size)
    else:
        plt.rc('font', size=15)

    if normalize:
        cm = cm.astype('float')/cm.sum(axis=1)[:,np.newaxis]
        if tit:
            title, fmt = tit, '.2f'
        else:
            title, fmt = 'Matriz de confusión normalizada', '.2f'
    else:
        if tit:
            title, fmt = tit, 'd'
        else:
            title, fmt = 'Matriz de confusión sin normalizar', 'd'
        cm = cm.astype(int)
    plt.figure(figsize=(14,14))
    if colors:
        plt.imshow(cm, interpolation='nearest', cmap = colors)
    else:
        plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title(title)
    plt.colorbar(shrink=0.75)
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=xtickRot)
    plt.yticks(tick_marks, classes)
    thresh = cm.max()/2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
#         print(j, i, format(cm[i, j]), fmt)
        plt.text(j, i, format(cm[i, j], fmt),horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")
    plt.tight_layout()
    if axisLabels:
        plt.ylabel(axisLabels[0])
        plt.xlabel(axisLabels[1])
    else:
        plt.ylabel('Clase Verdadera, yt')
        plt.xlabel('Clase Predicha, y')

    if png:
        plt.savefig(png + '.png', transparent=True, bbox_inches='tight')
    if pdf:
        plt.savefig(pdf + '.pdf', transparent=True, bbox_inches='tight')

    plt.show()

#-------------------------------------------------------------------------------#
def display_grid(rows, cols, xs, y_true, y_pred=None,
                 y_true_color='b', y_pred_color='g', figsize=(14, 7)):
    """Despliega ejemplos en una cuadrícula."""
    fig, ax = plt.subplots(rows, cols, figsize=figsize)
    i = 0
    for r in range(rows):
        for c in range(cols):
            img = xs[i]
            ax[r, c].imshow(xs[i], cmap='gray')
            ax[r, c].set_xticklabels([])
            ax[r, c].set_yticklabels([])
            x, y, w, h = y_true[i]
            rect = patches.Rectangle((x, y), w, h, linewidth=1,
                                     edgecolor=y_true_color,
                                     facecolor='none')
            ax[r, c].add_patch(rect)
            if y_pred is not None:
                img_h, img_w = img.shape[:2]
                x, y, w, h = y_pred[i]
                if x + w > img_w:
                    w = img_w - x
                if y + h > img_h:
                    h = img_h - y
                rect = patches.Rectangle((x, y), w, h, linewidth=1,
                                         edgecolor=y_pred_color,
                                         facecolor='none')
                ax[r, c].add_patch(rect)
            i += 1
    fig.tight_layout()
    plt.show()


def display_batch(rows, cols, x, y_true, y_pred=None,
                  y_true_color='b', y_pred_color='g', figsize=(14, 7)):
    """Despliega un lote en una cuadrícula."""
    # denormalizamos
    for c, (mean, std) in enumerate(zip(IMAGENET_MEAN, IMAGENET_STD)):
        x[:, c] = x[:, c] * std + mean
    x *= 255
    # rotamos canales
    x = x.permute(0, 2, 3, 1)
    # convertimos a entero
    x = (x.numpy()).astype(np.uint8)

    y_true = y_true.numpy().astype(np.uint8)
    if y_pred is not None:
        y_pred = y_pred.numpy().astype(np.uint8)
    display_grid(rows, cols, x, y_true, y_pred,
                 y_true_color=y_true_color,
                 y_pred_color=y_pred_color,
                 figsize=figsize)

def oneplot_multexps(df, title = None, axislabels = None, cpalette = 'Set1',smooth = False, png = False, pdf = False, style = 'seaborn-darkgrid', legendParams = ['upper center', (1.0,1.0)], fig_size = [12,10], fsizes = {'title':20, 'axes':20, 'legend':15, 'ticks':15}, x_axis = 'x'):
    # Initialize the figure style
    plt.style.use(style)

    # create a color palette
    n_cols = len(df.drop('x', axis = 1).columns)
    try:
        palette = plt.get_cmap(cpalette)
        c_av = len(palette.colors)
        if c_av > n_cols:
            palette = plt.get_cmap(cpalette, n_cols)
            c_av = len(palette.colors)
        else:
            palette = plt.get_cmap(cpalette)
    except:
        c_av = n_cols
        palette = plt.get_cmap(cpalette, c_av)

    fig, ax = plt.subplots(figsize=(fig_size[0], fig_size[1]))

    if not smooth:
        num=0
        for exp in df.drop('x', axis = 1):
            num += 1
            ax.plot(df.x, df[exp], label=exp, color=palette((num-1) % c_av))
    else:
        num=0
        for exp in df[df.drop('x', axis = 1).columns[:int((len(df.columns)-1)/2)]]:
            num += 1
            ax.plot(df.x, df[exp], label='_Hidden', color=palette((num-1) % c_av), alpha = smooth)
        num=0
        for exp in df[df.drop('x', axis = 1).columns[int((len(df.columns)-1)/2):]]:
            num += 1
            ax.plot(df.x, df[exp], label=exp[:-7], color=palette((num-1) % c_av))


    if axislabels:
        plt.xlabel(axislabels[0], fontsize=fsizes['axes'])
        plt.ylabel(axislabels[1], fontsize=fsizes['axes'])
    if title:
        plt.title(title, fontsize=fsizes['title'])
    if legendParams:
        plt.legend(fontsize=fsizes['legend'], loc=legendParams[0], bbox_to_anchor = legendParams[1], fancybox=True, shadow=True, ncol=4)
    else:
        plt.legend()

    plt.xticks(fontsize=fsizes['ticks'])
    plt.yticks(fontsize=fsizes['ticks'])

    if png:
        plt.savefig(png + '.png', transparent=True, bbox_inches='tight')
    if pdf:
        plt.savefig(pdf + '.pdf', transparent=True, bbox_inches='tight')

    plt.show()

def color_grid_plots(df, gridshape, title, axislabels = None, cpalette = 'Set1', smooth=False, png = False, pdf = False, style = 'seaborn-darkgrid', titleYloc = 0.98, fig_size = None, fsizes = False, x_axis = 'x'):
    if fsizes:
        for key,size in fsizes.items():
            if key == 'font':
                plt.rc(key, size=size)
            elif key == 'axes':
                plt.rc(key, titlesize=size)
                plt.rc(key, labelsize=size)
            elif key in ['xtick','ytick']:
                plt.rc(key, labelsize=size)
            elif key == 'legend':
                plt.rc(key, fontsize=size)
            elif key == 'figure':
                plt.rc(key, titlesize=size)

    # Initialize the figure style
    plt.style.use(style)

    # create a color palette
    n_cols = len(df.drop('x', axis = 1).columns)
    try:
        palette = plt.get_cmap(cpalette)
        c_av = len(palette.colors)
        if c_av > n_cols:
            palette = plt.get_cmap(cpalette, n_cols)
            c_av = len(palette.colors)
        else:
            palette = plt.get_cmap(cpalette)
    except:
        c_av = n_cols
        palette = plt.get_cmap(cpalette, c_av)


    # set figure size
    if fig_size:
        plt.figure(figsize=(fig_size[0], fig_size[1]))

    # multiple line plot
    num=0
    for column in df.drop(x_axis, axis=1):
        num+=1

        # Find the right spot on the plot
        plt.subplot(gridshape[0],gridshape[1], num)

        # plot every group, but discrete
        for v in df.drop(x_axis, axis=1):
            plt.plot(df[x_axis], df[v], marker='', color='grey', linewidth=0.6, alpha=0.3)

        # Plot the lineplot
        plt.plot(df[x_axis], df[column], marker='', color=palette((num-1) % c_av), linewidth=2.4, alpha=0.9, label=column)

        # Same limits for every chart
        # plt.xlim(0,500)
        # plt.ylim(-2,22)

        # Not ticks everywhere
        if num in range(7) :
            plt.tick_params(labelbottom='off')
        if num not in [1,4,7] :
            plt.tick_params(labelleft='off')

        # Add title
        if not smooth:
            plt.title(column, loc='left', fontsize=12, fontweight=0, color=palette((num-1) % c_av) )
        else:
            plt.title(column[:-7], loc='left', fontsize=12, fontweight=0, color=palette((num-1) % c_av) )
        if axislabels:
            plt.xlabel(axislabels[0])
            plt.ylabel(axislabels[1])

    # general title
    # plt.suptitle(title, fontsize=13, fontweight=0, color='black', style='italic', y=1.02)
    plt.suptitle(title, fontweight=0, color='black', style='italic', y = titleYloc)

    # # Axis titles
    # plt.text(0.5, 0.02, 'Time', ha='center', va='center')
    # plt.text(0.06, 0.5, 'Note', ha='center', va='center', rotation='vertical')

    if png:
        plt.savefig(png + '.png', transparent=True, bbox_inches='tight')
    if pdf:
        plt.savefig(pdf + '.pdf', transparent=True, bbox_inches='tight')

    # Show the graph
    plt.show()
