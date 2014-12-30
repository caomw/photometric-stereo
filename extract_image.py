def _parse_args():
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Extract images from a MVE scene')
    parser.add_argument('-i', '--image', help='Image Name', default='original')
    parser.add_argument('-f', '--format', help='Output File Format', default='jpg')
    parser.add_argument('scene', help='Scene Dir')
    parser.add_argument('output', help='Output Dir')
    return parser.parse_args()

from mve.core import Scene
from os.path import join, isdir
from os import mkdir
from PIL import Image

def extract_image(scene, image_name, output_dir, output_format = 'jpg'):
    for view in scene.views:
        if view.has_image(image_name):
            img = view.get_image(image_name)
            filename = "{} {}.{}".format(view.id, image_name, output_format)
            Image.fromarray(img).save(join(output_dir, filename))
        view.cleanup_cache()

def _prepare():
    global scene, ARGS
    ARGS = _parse_args()
    if not isdir(ARGS.output):
        mkdir(ARGS.output)
    scene = Scene(ARGS.scene)

def _run():
    global scene, ARGS
    extract_image(scene, ARGS.image, ARGS.output, ARGS.format)

if __name__ == '__main__':
    _prepare()
    _run()
