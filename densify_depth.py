def parse_args():
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Densify depth images')
    parser.add_argument('-i', '--input', help='Input Depth Name', default='depth-L1')
    parser.add_argument('-o', '--output', help='Output Depth Name', default='densedepth-L1')
    parser.add_argument('scene', help='Scene Dir')
    return parser.parse_args()

def densify(src):
    return src

def prepare():
    from mve.core import Scene
    global scene, ARGS
    ARGS = parse_args()
    scene = Scene(ARGS.scene)

def show(name, img):
    from cv2 import imshow, waitKey, destroyWindow
    from numpy import amin, amax, nonzero
    mindepth, maxdepth = amin(img[nonzero(img)]), amax(img)
    imshow(name, (img - mindepth) / (maxdepth - mindepth))
    waitKey(0)
    #destroyWindow(name)

def run():
    global scene, ARGS
    for view in scene.views:
        if view.has_image(ARGS.input):
            src = view.get_image(ARGS.input)
            dst = densify(src)
            show('test', dst)
            #view.set_image(ARGS.output, dst)
            #view.save()

if __name__ == '__main__':
    prepare()
    run()
