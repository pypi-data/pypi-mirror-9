from Numberjack import *
from pylab import *
from mpl_toolkits.basemap import Basemap
from matplotlib.text import Text, Annotation
from collections import defaultdict
from itertools import permutations, combinations


colours = ['red', 'blue', 'green', 'yellow']


def solvegraphcolouring(names, edges, k=4):
    model = Model()
    countyvariables = dict((name, Variable(k, name)) for name in names)

    for a, b in edges:
        model += countyvariables[a] != countyvariables[b]

    print model
    solver = model.load("Mistral")
    # solver = model.load("MiniSat")
    solver.solve()

    if not solver.is_sat():
        raise Exception("unsatisfied the model")

    d = {}
    for name, variable in countyvariables.iteritems():
        d[name] = colours[variable.get_value()]
    print d
    return d


def main():
    fig = plt.figure(figsize=(6, 10))
    # m = Basemap(llcrnrlon=-11.,llcrnrlat=50.5,urcrnrlon=-5.,urcrnrlat=56.,resolution='c',area_thresh=1000.,projection='tmerc',lon_0=-8.,lat_0=0.)
    # m = Basemap(llcrnrlon=-11.,llcrnrlat=50.5,urcrnrlon=-5.,urcrnrlat=56.,resolution='l',area_thresh=1000.,projection='tmerc',lon_0=-8.,lat_0=0.)
    m = Basemap(llcrnrlon=-11.,llcrnrlat=50.5,urcrnrlon=-5.,urcrnrlat=56.,resolution='i',area_thresh=1000.,projection='tmerc',lon_0=-8.,lat_0=0.)
    # m.drawcoastlines()
    # m.fillcontinents()
    # m.drawcountries(linewidth=2)
    # m.drawcounties()
    # # m.drawstates()
    # m.drawmapboundary(fill_color='aqua')
    m.drawmapboundary()

    # s = m.readshapefile('/Volumes/Samsung1TB/Downloads/ireland-and-northern-ireland-latest.shp/places', 'ireland')
    # s = m.readshapefile('/Volumes/Samsung1TB/Downloads/ireland-and-northern-ireland-latest.shp/natural', 'ireland')
    # s = m.readshapefile('/Volumes/Samsung1TB/Downloads/ireland-and-northern-ireland-latest.shp/landuse', 'ireland')
    # s = m.readshapefile('/Volumes/Samsung1TB/Downloads/ireland-and-northern-ireland-latest.shp/points', 'ireland')

    # s = m.readshapefile('./shp/Census2011_Province_generalised20m', 'ireland')
    # s = m.readshapefile('./shp/Census2011_Admin_Counties_generalised20m', 'ireland')
    # s = m.readshapefile('./IRL_adm/IRL_adm0', 'ireland')
    s = m.readshapefile('./IRL_adm/IRL_adm1', 'ireland', drawbounds=False)

    # Extract the neighbours by building sets of coordinates and finding
    # non-empty set intersections. Each named location may have multiple lists of
    # points so we build a single universal set for each named location.
    countypoints = defaultdict(set)
    for xy, info in zip(m.ireland, m.ireland_info):
        countypoints[info['NAME_1']].update(xy)

    allnames = list(sorted(countypoints.keys()))
    neighbours = []
    for a, b in combinations(allnames, 2):
        intersec = countypoints[a].intersection(countypoints[b])
        # print a, b, len(intersec)
        if intersec:
            neighbours.append((a, b))

    # Solve the graph colouring problem
    colourmap = solvegraphcolouring(allnames, neighbours)

    # Plot the result
    for xy, info in zip(m.ireland, m.ireland_info):
        name = info['NAME_1']
        colour = colourmap[name] if name in colourmap else 'gray'
        poly = Polygon(xy, facecolor=colour, alpha=0.4)
        plt.gca().add_patch(poly)

    # def drawni():
    #     # s = m.readshapefile('./GBR_adm/GBR_adm2', 'ireland', drawbounds=False)
    #     names = set()
    #     for xy, info in zip(m.ireland, m.ireland_info):
    #         # name = info['NAME_1']
    #         name = info['NAME_2']
    #         names.add(name)
    #         if name in ['Derry', 'Down', 'Fermanagh', 'Antrim']:
    #             print len(xy), info
    #             colour = colourmap[name] if name in colourmap else 'gray'
    #             poly = Polygon(xy, facecolor=colour, alpha=0.4)
    #             plt.gca().add_patch(poly)

        # plt.text(xy[0][0], xy[0][1], info['NAME_1'])
        # print (xy[0], xy[1], info['NAME_1'],)

    # plt.legend()
    # plt.show()
    # plt.savefig("basemaptest.pdf", bbox_inches='tight')
    plt.savefig("basemaptest.jpg")


if __name__ == '__main__':
    main()


