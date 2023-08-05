from .outdated_list import OutdatedList
from argparse import ArgumentParser


def main():
    parser = ArgumentParser('pip_extras',
                            'Provides functionality for updating all your ' +
                            'outdated packages')

    parser.add_argument('-d', '--dry', '--dry-run',
                        dest="dry_run", default=False,
                        action="store_true",
                        help="Do not do anything, just print what would be done.")

    parser.add_argument('packages', nargs='*',
                        metavar="PACKAGE_NAME",
                        help="Name of package to update - without specifying a " +
                        "package all packages will be updated.")

    options = parser.parse_args()
    cmd = OutdatedList()
    for name, local, remote in cmd.outdated:
        if (not options.packages) or name in options.packages:
            if options.dry_run:
                print("Would update {0} {1} -> {2}".format(
                    name, cmd.display_version(local), cmd.display_version(remote)))
            else:
                cmd.update(name)

if __name__ == '__main__':
    main()