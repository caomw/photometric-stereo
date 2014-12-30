def parse_args():
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Extract images from a MVE scene')
    parser.add_argument('-i', '--image', help='Image Name', default='original')
    parser.add_argument('-f', '--format', help='Output File Format', default='jpg')
    parser.add_argument('scene', help='Scene Dir')
    parser.add_argument('output', help='Output Dir')
    return parser.parse_args()

ARGS = parse_args()

from mve.core import Scene
from os.path import join, isdir
from os import mkdir
from PIL import Image

def prepare():
    global scene, ARGS
    if not isdir(ARGS.output):
        mkdir(ARGS.output)
    scene = Scene(ARGS.scene)

def run():
    global scene, ARGS
    for view in scene.views:
        if view.has_image(ARGS.image):
            img = view.get_image(ARGS.image)
            filename = "{} {}.{}".format(view.id, ARGS.image, ARGS.format)
            Image.fromarray(img).save(join(ARGS.output, filename))
        view.cleanup_cache()

if __name__ == '__main__':
    prepare()
    run()
