def parse_args():
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Reduce Noise of Pointset (PCL)')
    parser.add_argument('input', help='Input Noisy Point Cloud')
    parser.add_argument('output', help='Output Point Cloud')
    return parser.parse_args()

def prepare():
    global ARGS
    ARGS = parse_args()

def run():
    global ARGS
    import pcl
    pset = pcl.load(ARGS.input)
    fil = p.make_statistical_outlier_filter()
    fil.set_mean_k(20)
    fil.set_std_dev_mul_thresh(1.0)
    pcl.save(fil.filter(), ARGS.output)

if __name__ == '__main__':
    prepare()
    run()
