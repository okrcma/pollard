import os
from walk import PolynomialFunction, GeneralWalk
import random
import logging
import json

logger = logging.getLogger("CurveGraph")
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')

# set sage variables if not already set so that the script can run in directly in the python interpreter
if 'SAGE_ROOT' not in os.environ:
    os.environ['SAGE_ROOT'] = '/usr/share/sagemath'
    logger.info("Setting 'SAGE_ROOT' to '{}'.".format(os.environ['SAGE_ROOT']))
if 'SAGE_LOCAL' not in os.environ:
    os.environ['SAGE_LOCAL'] = '/usr/share/sagemath'
    logger.info("Setting 'SAGE_LOCAL' to '{}'.".format(os.environ['SAGE_LOCAL']))


import sage.all as sg


class CurveGraph:
    def __init__(self, curve, walk, points, pindex, fedges, bedges):
        logger.info("Initializing the graph...")

        self.curve = curve
        self.walk = walk
        self.points = points
        self.pindex = pindex
        self.fedges = fedges
        self.bedges = bedges

        logger.info("... finished initializing.")

    @classmethod
    def map_curve(cls, curve, walk):
        logger.info("Mapping curve {} with walk {}...".format(curve, walk))

        logger.info("Getting curve points.".format(curve, walk))
        points = curve.points()
        logger.info("Indexing curve points.".format(curve, walk))
        pindex = {points[i]: i for i in range(0, len(points))}

        # FIXME takes the most time
        logger.info("Getting forward edges.".format(curve, walk))
        fedges = [pindex[walk.next_point(p)] for p in points]

        logger.info("Getting backward edges.".format(curve, walk))
        bedges = [[] for _ in range(0, len(points))]
        for i in range(0, len(fedges)):
            j = fedges[i]
            bedges[j].append(i)

        logger.info("... finished mapping the curve.")
        return cls(curve, walk, points, pindex, fedges, bedges)

    def get_cycle(self, vertices):
        # logger.info("Computing a cycle...")

        x = vertices[0]
        visited = []
        while x not in visited:
            visited.append(x)
            x = self.fedges[x]
        i = visited.index(x)
        path = visited[:i]
        cycle = visited[i:]

        # logger.info("... finished computing a cycle...")
        return cycle

    def get_component(self, cycle):
        # logger.info("Computing a component...")

        component = []
        stack = [(x, 0) for x in cycle]
        distances = []
        c = 0
        while len(stack) > 0:
            c += 1
            if c > len(self.points):
                raise RuntimeError

            x, d = stack.pop()
            component.append(x)
            if len(distances) <= d:
                distances.append(0)
            distances[d] += 1
            for y in self.bedges[x]:
                if y not in cycle:
                    stack.append((y, d+1))

        # logger.info("... finished computing a component")
        return component, distances

    def analyze(self):
        logger.info("Analyzing the graph...")

        unvisited = list(range(0, len(self.points)))
        stats = {
            "graph_size": len(self.points),
            "num_components": None,
            "components": [],
        }
        while len(unvisited) > 0:
            cycle = self.get_cycle(unvisited)
            component, distances = self.get_component(cycle)

            component_stats = {
                "component_size": len(component),
                "period": len(cycle),
            }

            total_distance = 0
            for i in range(1, len(distances)):
                total_distance += i * distances[i]
            avg_preperiod = 0 if total_distance == 0 else total_distance / sum(distances[1:])
            max_preperiod = len(distances)-1
            component_stats["avg_preperiod"] = avg_preperiod
            component_stats["max_preperiod"] = max_preperiod

            component_stats["distances"] = distances

            stats["components"].append(component_stats)

            for x in component:
                unvisited.remove(x)  # FIXME probably not logarithmic

        stats["num_components"] = len(stats["components"])

        logger.info("... finished analyzing the graph.")
        return stats


if __name__ == "__main__":
    print("hello")

    gf = sg.GF(1009)
    e = sg.EllipticCurve(gf, [1, 2])

    s = e.random_point()
    k = random.randint(0, s.order() - 1)
    t = k * s

    x, y = gf["x", "y"].gens()
    p_s = x+y
    p_t = x*y

    g_s = PolynomialFunction(p_s, 2).eval
    g_t = PolynomialFunction(p_t, 2).eval

    # n = s.order()
    # g_s = g_t = lambda _: random.randint(0, n-1)
    w = GeneralWalk(s=s, t=t, g_s=g_s, g_t=g_t)

    graph = CurveGraph.map_curve(e, w)
    stats = graph.analyze()
    print(json.dumps(stats, indent=2))
