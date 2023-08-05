__all__ = ['tsort']
from functools import reduce

def tsort(data, smallest_first=False, fewest_edges_first=False, flatten=False):
    # FIXME: support fewest_edges_first

    # make copy of data
    tmp = data.copy()

    # remove self-references
    for k, v in tmp.items():
        v.discard(k)

    # initially find vertices that do not point to anything
    all_vertices = reduce(set.union, tmp.values())
    starting_vertices = set(tmp.keys())
    empty_vertices = all_vertices - starting_vertices

    # insert empty vertices
    for k in empty_vertices:
        tmp[k] = set()

    # algorithm starts here
    sorted_vertices = []

    while True:
        # get all vertices that do not point to anything
        empty_vertices = {k for k, v in tmp.items() if not v}

        if not empty_vertices:
            break

        # if required, sort by smallest-numbered available vertex first
        if smallest_first:
            _empty_vertices = sorted(empty_vertices)
        else:
            _empty_vertices = (v for v in empty_vertices)

        # add current vertices that do not point to any other vertices
        if flatten:
            sorted_vertices.extend(_empty_vertices)
        else:
            sorted_vertices.append(_empty_vertices)

        # traverse all vertices and take set difference for
        # vertices which are not in previously found vertices
        # that do not point to any other vertices
        
        # tmp = {
        #     k: (v - empty_vertices)
        #     for k, v in tmp.items()
        #     if k not in empty_vertices
        # }

        for k, v in list(tmp.items()):
            if k in empty_vertices:
                del tmp[k]
            else:
                tmp[k] = v - empty_vertices

    if tmp:
        raise ValueError('Cyclic dependencies found')

    return sorted_vertices

if __name__ == '__main__':
    from pprint import pprint

    data = {
        2: {11},
        9: {11, 8},
        10: {11, 3},
        11: {7, 5},
        8: {7, 3},
    }

    out = tsort(data, smallest_first=True)
    pprint(out)