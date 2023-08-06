from Numberjack import *
from pylab import *
from mpl_toolkits.basemap import Basemap
from matplotlib.text import Text, Annotation
from collections import defaultdict
from itertools import permutations, combinations


def solvegraphcolouring(names, edges, colours=['red', 'blue', 'green', 'yellow']):
    model = Model()
    regionvariables = {}

    # Create the variables for each region which take one of the 'colours'
    for name in names:
        regionvariables[name] = Variable(colours, name)

    # Disequalities between regions
    for a, b in edges:
        model += regionvariables[a] != regionvariables[b]

    print model
    solver = model.load("Mistral")
    solver.solve()

    if not solver.is_sat():
        raise Exception("unsatisfied the model")

    d = {}
    for name, variable in regionvariables.iteritems():
        d[name] = variable.get_value()

    return d


def main():
    fig = plt.figure(figsize=(6, 9))
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
        poly = Polygon(xy, facecolor=colour, alpha=0.4)
        plt.gca().add_patch(poly)

    # plt.savefig("MapColouringIreland.pdf", bbox_inches='tight')
    plt.savefig("MapColouringIreland.jpg")
    plt.show()


if __name__ == '__main__':
    main()
