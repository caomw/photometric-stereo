def parse_args():
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Reduce Noise of Pointset')
    parser.add_argument('fine_pointset', help='Fine Point Cloud (Low Level)')
    parser.add_argument('noisy_pointset', help='Noisy Point Cloud (High Level)')
    parser.add_argument('output_pointset', help='Output Point Cloud')
    return parser.parse_args()

class Mesh:
    def __init__(self, filename):
        from plyfile import PlyData
        from numpy import transpose
        meshdata = PlyData.read(filename)
        data = meshdata['vertex'].data
        positions = transpose([data['x'], data['y'], data['z']])
        self.meshdata = meshdata
        self.positions = positions

    def build_kdtree(self):
        from scipy.spatial import KDTree
        self.kdtree = KDTree(self.positions, leafsize=100)

    def knn(self, points, k=1):
        import numpy as np
        return self.kdtree.query(points, k, p=2)

def prepare():
    global ARGS
    ARGS = parse_args()
    import sys
    from os.path import join, dirname, abspath
    root = dirname(abspath(__file__))
    sys.path.append(join(root, 'plyfile'))

    global fine_mesh, noisy_mesh
    fine_mesh = Mesh(ARGS.fine_pointset)
    noisy_mesh = Mesh(ARGS.noisy_pointset)

    fine_mesh.build_kdtree()

def run():
    global ARGS, fine_mesh, noisy_mesh

    # Run K-Nearest Neighbour
    distances, indices = fine_mesh.knn(noisy_mesh.positions)
    selector = distances < 0.01

    # Load Old Data
    vertex_element = noisy_mesh.meshdata['vertex']
    print('Number of Vertex in Noisy Point Cloud: %d' % vertex_element.data.size)

    # Create New Data
    from plyfile import PlyElement, PlyData
    new_element = PlyElement.describe(vertex_element.data[selector], 'vertex')
    print('Number of Vertex in Output Point Cloud: %d' % new_element.data.size)
    PlyData([new_element]).write(ARGS.output_pointset)

if __name__ == '__main__':
    prepare()
    run()
