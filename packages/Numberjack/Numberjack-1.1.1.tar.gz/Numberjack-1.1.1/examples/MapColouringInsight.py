from Numberjack import *
from pylab import *
from mpl_toolkits.basemap import Basemap
from matplotlib.text import Text, Annotation
from collections import defaultdict
from itertools import permutations, combinations


def rgbtohex(r, g, b):
    return '#%02x%02x%02x' % (r, g, b)


colours = ['red', 'blue', 'green', 'yellow']

insightblue = rgbtohex(0, 107, 148)
insightgreen = rgbtohex(76, 183, 72)
insightforestgreen = rgbtohex(0, 105, 106)
insightorange = rgbtohex(246, 135, 31)
insightburntorange = rgbtohex(193, 49, 34)
insightplum = rgbtohex(105, 44, 122)
insightpurple = rgbtohex(61, 91, 169)
insightpink = rgbtohex(186, 52, 111)
insightbabyblue = rgbtohex(176, 215, 227)

# insightcolours = [insightblue, insightgreen, insightorange, insightburntorange, insightplum, insightbabyblue]
insightcolours = [insightplum, insightforestgreen, insightpurple, insightpink]


def solvegraphcolouring(names, edges, k=4):
    model = Model()
    countyvariables = dict((name, Variable(k, name)) for name in names)

    for a, b in edges:
        model += countyvariables[a] != countyvariables[b]

    print model
    solver = model.load("Mistral")
    solver.solve()

    if not solver.is_sat():
        raise Exception("unsatisfied the model")

    d = {}
    for name, variable in countyvariables.iteritems():
        # d[name] = colours[variable.get_value()]
        d[name] = insightcolours[variable.get_value()]
    return d


def main():
    fig = plt.figure(figsize=(12, 18))
    m = Basemap(llcrnrlon=-11.0, llcrnrlat=51.2,
                urcrnrlon=-5.5, urcrnrlat=55.7,
                resolution='i', area_thresh=1000.,
                projection='tmerc', lon_0=-8., lat_0=0.)
    m.drawmapboundary()

    s = m.readshapefile('./IRL_adm/IRL_adm1', 'ireland', drawbounds=False)

    # Extract the neighbours by building sets of coordinates and finding
    # non-empty set intersections. Each named location may have multiple lists of
    # points so we build a single universal set for each named location.
    regionpoints = defaultdict(set)
    for xy, info in zip(m.ireland, m.ireland_info):
        regionpoints[info['NAME_1']].update(xy)

    allnames = list(sorted(regionpoints.keys()))  # Extract region names
    neighbours = []
    for a, b in combinations(allnames, 2):
        intersec = regionpoints[a].intersection(regionpoints[b])
        if intersec:
            neighbours.append((a, b))

    # Solve the graph colouring problem
    colourmap = solvegraphcolouring(allnames, neighbours)
    print colourmap

    # Plot the result
    print "Plotting..."
    for xy, info in zip(m.ireland, m.ireland_info):
        name = info['NAME_1']
        colour = colourmap[name] if name in colourmap else 'gray'
        poly = Polygon(xy, facecolor=colour, alpha=0.7)
        # poly = Polygon(xy, facecolor="white", alpha=1.0)
        plt.gca().add_patch(poly)

    plt.savefig("MapColouringIreland_clear.pdf", bbox_inches='tight')
    # plt.savefig("MapColouringIreland.rgba")


if __name__ == '__main__':
    main()
