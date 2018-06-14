from astro_tools_web.lib.fits_index import FitsIndex


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='root path containing fits files')
    args = parser.parse_args()

    index = FitsIndex(args.path)
    index.reindex_path()
    index.write_index()


if __name__ == '__main__':
    main()
