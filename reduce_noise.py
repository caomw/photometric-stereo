def parse_args():
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Reduce Noise of Pointset')
    parser.add_argument('fine_pointset', help='Fine Point Cloud (Low Level)')
    parser.add_argument('coarse_pointset', help='Rough Point Cloud (High Level)')
    parser.add_argument('output_pointset', help='Output Point Cloud')
    return parser.parse_args()

def prepare():
    global ARGS
    ARGS = parse_args()
    import sys
    from os.path import join, dirname, abspath
    root = dirname(abspath(__file__))
    sys.path.append(join(root, 'plyfile'))

def run():
    global ARGS
    from plyfile import PlyData
    fine_mesh = PlyData.read(ARGS.fine_pointset)
    rough_mesh = PlyData.read(ARGS.coarse_pointset)
    fine_mesh['vertex'].data['x']
    fine_mesh['vertex'].data['y']
    fine_mesh['vertex'].data['z']

if __name__ == '__main__':
    prepare()
    run()

