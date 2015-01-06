def parse_args():
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Render Point Cloud to Views')
    parser.add_argument('-v', '--views', help='Selected Views', nargs='*', type=int)
    parser.add_argument('--width', help='Width of Canvas', type=int, default=600)
    parser.add_argument('--height', help='Height of Canvas', type=int, default=400)
    parser.add_argument('scene', help='Scene Directory')
    parser.add_argument('input', help='Input Point Cloud')
    return parser.parse_args()

def prepare():
    global ARGS
    ARGS = parse_args()

    import sys
    from os.path import join, dirname, abspath
    root = dirname(abspath(__file__))
    sys.path.append(join(root, 'plyfile'))

    global scene
    from mve.core import Scene
    scene = Scene(ARGS.scene)

    global mesh
    from plyfile import PlyData
    mesh = PlyData.read(ARGS.input)

def get_view_transformation(view, width, height):
    global ARGS
    import numpy as np

    cam = view.camera
    view_mat = cam.world_to_cam_matrix

    proj_mat = np.zeros((4,4), dtype=np.float32)
    proj_mat[0:3,0:3] = cam.get_calibration(width, height)
    proj_mat[3,:] = [0,0,1,0]

    return np.dot(proj_mat, view_mat)

def run():
    global ARGS, scene, mesh
    import numpy as np

    # Load vertices
    vertex_element = mesh['vertex']
    num_vert = vertex_element.data.size

    # Create View Array
    views = scene.views
    if ARGS.views:
        views = filter(lambda v: v.id in ARGS.views, views)

    # Create Vertex Array
    positions = np.empty((4, num_vert), dtype=np.float32)
    positions[0,:] = vertex_element.data['x']
    positions[1,:] = vertex_element.data['y']
    positions[2,:] = vertex_element.data['z']
    positions[3,:] = 1.0
    colors = np.empty((num_vert, 3), dtype=np.uint8)
    colors[:,0] = vertex_element.data['red']
    colors[:,1] = vertex_element.data['green']
    colors[:,2] = vertex_element.data['blue']

    # Filter out vertices for each view
    for view in views:
        width, height = ARGS.width, ARGS.height
        txfm = get_view_transformation(view, width, height)

        tcoords = np.dot(txfm, positions)
        np.divide(tcoords, tcoords[3,:], output=tcoords)
        np.subtract(tcoords, 0.5, output=tcoords)
        tcoords = tcoords[1::-1,:]
        #print(tcoords)

        canvas = np.zeros((height, width, 3), dtype=np.uint8)

        for vid in xrange(0, num_vert):
            i, j = tcoords[0][vid], tcoords[1][vid]
            if i < 0 or j < 0 or i >= height or j >= width:
                continue
            canvas[i, j] = colors[vid]

        from cv2 import imshow, cvtColor, COLOR_RGB2BGR, waitKey
        imshow('View %d' % view.id, cvtColor(canvas, COLOR_RGB2BGR))
        waitKey(1)

        view.cleanup_cache()

    # Pause
    from cv2 import waitKey
    waitKey(0)


if __name__ == '__main__':
    prepare()
    run()

# python render_points.py -v 0 1 2 -- tmp/e100vs/scene-L5 tmp/e100vs/pset-L5.ply
