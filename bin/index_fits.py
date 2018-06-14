from astro_tools_web.lib.fits_index import FitsIndex


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='root path containing fits files')
    args = parser.parse_args()

    index = FitsIndex(args.path)

    for fn in iglob(join(args.path, '**/*.fits')):
        index.index_file(fn)

    index.write_index(args.index_fn)


if __name__ == '__main__':
    main()
