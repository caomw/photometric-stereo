def parse_args():
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Extract images from a MVE scene')
    parser.add_argument('--show', help='Show Window', default=False, action='store_true')
    parser.add_argument('-i', '--image', help='Image Name', default='original')
    parser.add_argument('-f', '--format', help='Output File Format', default='jpg')
    parser.add_argument('scene', help='Scene Dir')
    parser.add_argument('output', help='Output Dir')
    return parser.parse_args()

ARGS = parse_args()

from mve.core import Scene
from os.path import join, isdir
from os import mkdir
from cv2 import imwrite, cvtColor, COLOR_RGB2BGR

if ARGS.show:
    from cv2 import imshow, waitKey, destroyWindow

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
            if len(img.shape) == 3 and img.shape[2] == 3:
                img = cvtColor(img, COLOR_RGB2BGR)
            filename = "{} {}.{}".format(view.id, ARGS.image, ARGS.format)
            imwrite(join(ARGS.output, filename), img)
            if ARGS.show:
                imshow(filename, img)
                waitKey(0)
                destroyWindow(filename)
        view.cleanup_cache()

if __name__ == '__main__':
    prepare()
    run()
