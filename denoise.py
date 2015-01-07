def parse_args():
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Reduce Noise of Pointset')
    parser.add_argument('-i', '--image', help='Image Name', default='undistorted')
    parser.add_argument('-v', '--views', help='Selected Views', nargs='*', type=int)
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
    if ARGS.views:
        views = filter(lambda v: v.id in ARGS.views, views)
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
    #selector = np.ones(num_vert, dtype=np.bool)
    counter = np.zeros(num_vert, dtype=np.int32)
    passer = np.zeros(num_vert, dtype=np.int32)

    # Filter out vertices for each view
    for view in views:
        txfm = get_view_transformation(view)
        image = view.get_image(ARGS.image)
        width, height = image.shape[1], image.shape[0]

        tcoords = np.dot(txfm, positions)
        np.divide(tcoords, tcoords[3,:], output=tcoords)
        np.subtract(tcoords, 0.5, output=tcoords)
        tcoords = tcoords[1::-1,:]
        #print(tcoords)

        visibility = np.logical_and(tcoords[0] >= 0, tcoords[1] >= 0)
        np.logical_and(visibility, (tcoords[0] < height), out=visibility)
        np.logical_and(visibility, (tcoords[1] < width), out=visibility)
        #print('visibility:', visibility.shape)

        tcolors = np.empty((num_vert, 3), dtype=np.int32)
        for vid in xrange(0, num_vert):
            i, j = tcoords[0][vid], tcoords[1][vid]
            if not visibility[vid]:
                continue
            tcolors[vid,:] = np.subtract(image[i, j], colors[vid])

        np.square(tcolors, out=tcolors)
        diff = np.sum(tcolors, axis=1)
        #print('diff:', diff)
        #diff = tdiffs
        #print(diff)

        selector = np.logical_and(diff < 100, visibility)
        counter[visibility] += 1
        passer[selector] += 1

        # TODO: Occlusion Problem
        #   Some correct points are actually occluded by other surfaces in some views
        #   It's hard for the program to determine occluded correct points and wrong points
        #
        # Possible Solution:
        #   Use dense depth map for depth testing
        #   If the depth value of the point is greater than the depth map, the point is occluded
        #
        print('view[%d]: (%d/%d) passed' % (view.id, np.count_nonzero(selector), np.count_nonzero(visibility)))

        del image
        view.cleanup_cache()

    # Determine Selector
    selector = np.zeros(num_vert, dtype=np.bool)
    selector[ np.add(passer, passer) > counter ] = True

    # Extract vertices filtered
    from plyfile import PlyElement, PlyData
    new_element = PlyElement.describe(vertex_element.data[selector], 'vertex')
    print('Number of Vertex in Output Point Cloud: %d' % new_element.data.size)
    PlyData([new_element]).write(ARGS.output)

if __name__ == '__main__':
    prepare()
    run()
