def parse_args():
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Structure for Motion View')
    parser.add_argument('scene', help='Scene Dir')
    return parser.parse_args()

def run(scene):
    pass

if __name__ == '__main__':
    from mve.core import Scene
    global ARGS
    ARGS = parse_args()
    scene = Scene(ARGS.scene)
    run(scene)
