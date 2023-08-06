from __future__ import print_function

import sys


class Vertex:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z
        self.key = (float(x), float(y), float(z))


class Normal:
    def __init__(self, dx, dy, dz):
        self.dx, self.dy, self.dz = dx, dy, dz


class Facet:
    def __init__(self, normal, v1, v2, v3):
        self.normal = normal
        if v1.key < v2.key:
            if v1.key < v3.key:
                self.vertices = (v1, v2, v3)  # v1 is the smallest
            else:
                self.vertices = (v3, v1, v2)  # v3 is the smallest
        else:
            if v2.key < v3.key:
                self.vertices = (v2, v3, v1)  # v2 is the smallest
            else:
                self.vertices = (v3, v1, v2)  # v3 is the smallest

    def key(self):
        return (self.vertices[0].x, self.vertices[0].y, self.vertices[0].z,
                self.vertices[1].x, self.vertices[1].y, self.vertices[1].z,
                self.vertices[2].x, self.vertices[2].y, self.vertices[2].z)


class STL:
    def __init__(self, fname):
        self.facets = []

        f = open(fname)
        words = [s.strip() for s in f.read().split()]
        f.close()

        if words[0] == 'solid':
            i = 1
            while words[i] != 'facet':
                i = i+1
            while words[i] == 'facet':
                norm = Normal(words[i + 2],  words[i + 3],  words[i + 4])
                v1 = Vertex(words[i + 8],  words[i + 9],  words[i + 10])
                v2 = Vertex(words[i + 12], words[i + 13], words[i + 14])
                v3 = Vertex(words[i + 16], words[i + 17], words[i + 18])
                i += 21
                self.facets.append(Facet(norm, v1, v2, v3))

            self.facets.sort(key=Facet.key)
        else:
            print("Not an ascii STL file")
            sys.exit(1)

    def write(self, fname):
        f = open(fname, "wt")
        print('solid model', file=f)
        for facet in self.facets:
            print('  facet normal %s %s %s' %
                  (facet.normal.dx, facet.normal.dy, facet.normal.dz), file=f)
            print('    outer loop', file=f)
            for vertex in facet.vertices:
                print('      vertex %s %s %s' %
                      (vertex.x, vertex.y, vertex.z), file=f)
            print('    endloop', file=f)
            print('  endfacet', file=f)
        print('endsolid model', file=f)
        f.close()


def canonicalise(fname):
    stl = STL(fname)
    stl.write(fname)


def main():
    if len(sys.argv) >= 2:
        error = False
        for stl in sys.argv[1:]:
            try:
                canonicalise(stl)
            except Exception as e:
                sys.stderr.write(str(e))
                sys.stderr.write('\n')
                error = True
        if error:
            sys.exit(1)
    else:
        print("usage: stlsort file.stl [file2.stl [...]]")
        sys.exit(1)

if __name__ == '__main__':
    main()
