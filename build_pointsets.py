def parse_args():
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Generate Pointsets with different levels')
    parser.add_argument('-m', '--mesh', help='Output Name', default='pointset')
    parser.add_argument('-l', '--level', help='Maximum Levels', default=5, type=int)
    parser.add_argument('scene', help='Scene Dir')
    parser.add_argument('output', help='Output Dir')
    return parser.parse_args()

from os.path import isdir, join
from os import mkdir

def prepare():
    global ARGS
    ARGS = parse_args()

    if not isdir(ARGS.output):
        mkdir(ARGS.output)

    input_path = join(ARGS.output, 'input')
    if not isdir(input_path):
        mkdir(input_path)

    from mve.core import Scene
    from extract_image import extract_image
    scene = Scene(ARGS.scene)
    extract_image(scene, 'original', input_path)
    del scene

def run_each_level(level):
    global ARGS
    from subprocess import call
    scene_name = 'scene-L%d' % level
    scene_path = join(ARGS.output, scene_name)
    mesh_name = '%s-L%d.ply' % (ARGS.mesh, level)
    mesh_path = join(ARGS.output, mesh_name)
    call(['mve-makescene', '-i', join(ARGS.output, 'input'), scene_path])
    call(['mve-sfmrecon', scene_path])
    call(['mve-dmrecon', '-s%d' % level, scene_path])
    call(['mve-scene2pset', '-F%d' % level, scene_path, mesh_path])

def run():
    global ARGS
    for level in xrange(1, ARGS.level+1):
        run_each_level(level)

if __name__ == '__main__':
    prepare()
    run()
