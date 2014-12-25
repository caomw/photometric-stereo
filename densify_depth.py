def parse_args():
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Densify depth images')
    parser.add_argument('-c', '--color', help='Input Color Name', default='undist-L1')
    parser.add_argument('-i', '--input', help='Input Depth Name', default='depth-L1')
    parser.add_argument('-o', '--output', help='Output Depth Name', default='densedepth-L1')
    parser.add_argument('scene', help='Scene Dir')
    return parser.parse_args()

def prepare():
    from mve.core import Scene
    global scene, ARGS
    ARGS = parse_args()
    scene = Scene(ARGS.scene)

def show(name, img, wait=True):
    from cv2 import imshow, waitKey, destroyWindow
    from numpy import amin, amax, nonzero
    img_nonzero = img[nonzero(img)]
    mindepth, maxdepth = amin(img_nonzero), amax(img_nonzero)
    imshow(name, (img - mindepth) / (maxdepth - mindepth))
    if wait:
        waitKey(0)
    #destroyWindow(name)

def densify(color, src):
    from cv2 import imshow
    from scipy.ndimage.filters import convolve1d
    from numpy import nonzero
    import numpy as np
    mask = np.zeros(src.shape, dtype=np.uint8)
    mask[nonzero(src)] = 255
    #imshow('mask', mask)
    d2x = convolve1d(src, [-1, 2, -1], 1)
    d2y = convolve1d(src, [-1, 2, -1], 0)
    #show('d2x', d2x, False)
    #show('d2y', d2y, False)
    return src

def run():
    global scene, ARGS
    for view in scene.views:
        if view.has_image(ARGS.input) and view.has_image(ARGS.color):
            color = view.get_image(ARGS.color)
            src = view.get_image(ARGS.input)
            dst = densify(src)
            show('test', dst)
            #view.set_image(ARGS.output, dst)
            #view.save()
        view.cleanup_cache()

if __name__ == '__main__':
    prepare()
    run()
