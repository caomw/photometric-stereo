def parse_args():
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Reduce Noise of Pointset')
    parser.add_argument('-i', '--image', help='Image Name', default='undistorted')
    parser.add_argument('scene', help='Scene Directory')
    parser.add_argument('input', help='Input Noisy Point Cloud')
    parser.add_argument('output', help='Output Point Cloud')
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

    global noisy_mesh
    from plyfile import PlyData
    noisy_mesh = PlyData.read(ARGS.input)

def get_view_transformation(view):
    global ARGS
    import numpy as np

    cam = view.camera
    image = view.get_image(ARGS.image)
    width, height = image.shape[1], image.shape[0]

    view_mat = cam.world_to_cam_matrix

    proj_mat = np.zeros((4,4), dtype=np.float32)
    proj_mat[0:3,0:3] = cam.get_calibration(width, height)
    proj_mat[3,:] = [0,0,1,0]

    return np.dot(proj_mat, view_mat)

def run():
    global ARGS, scene, noisy_mesh
    import numpy as np

    # Load vertices
    vertex_element = noisy_mesh['vertex']
    num_vert = vertex_element.data.size
    print('Number of Vertex in Noisy Point Cloud: %d' % num_vert)

    # Create View Array
    views = scene.views
    #view_txfms = map(get_view_transformation, views)
    #view_images = map(lambda v: v.get_image(ARGS.image), views)

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

    # Prepare filter list
    selector = np.ones(num_vert, dtype=np.bool)

    # Filter out vertices for each view
    for view in views:
        txfm = get_view_transformation(view)
        image = view.get_image(ARGS.image)
        width, height = image.shape[1], image.shape[0]

        tpos = np.dot(txfm, positions)
        np.divide(tpos, tpos[3,:], output=tpos)
        np.subtract(tpos, 0.5, output=tpos)
        tx, ty = tpos[0,:], tpos[1,:]

        tcoords = tpos[1::-1,:]

        visibility = np.logical_and(tcoords[0,:] >= 0, tcoords[1,:] >= 0)
        np.logical_and(visibility, (tcoords[0,:] < height), out=visibility)
        np.logical_and(visibility, (tcoords[1,:] < width), out=visibility)

        tcoords_clipped = np.empty((2, num_vert), dtype=np.float32)
        np.clip(tcoords[0], 0, height-1, out=tcoords_clipped[0,:])
        np.clip(tcoords[1], 0, width-1, out=tcoords_clipped[1,:])

        np.floor(tcoords_clipped, out=tcoords_clipped)
        tcolors = image[np.array(tcoords_clipped, dtype=np.int32)]

        #tcolors = np.empty((num_vert, 3), dtype=np.int16)
        #for vid in np.ndindex(num_vert):
        #    if not visibility[vid]:
        #        tcolors[vid,:] = colors[vid]
        #    else:
        #        i, j = np.floor(ty[vid]), np.floor(tx[vid])
        #        tcolors[vid,:] = image[i, j]

        diff3 = np.subtract(tcolors, colors)
        np.square(diff3, out=diff3)
        diff = np.sum(diff3, axis=1)
        #print(diff)

        #np.logical_or(diff < 500, np.logical_not(t_inside))
        np.logical_and(selector, diff < 500, out=selector)
        print('Selector: %d passed' % np.count_nonzero(selector))

    # Extract vertices filtered
    from plyfile import PlyElement, PlyData
    new_element = PlyElement.describe(vertex_element.data[selector], 'vertex')
    print('Number of Vertex in Output Point Cloud: %d' % new_element.data.size)
    PlyData([new_element]).write(ARGS.output)

if __name__ == '__main__':
    prepare()
    run()
