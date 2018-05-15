import os.path
import sys
import argparse

#logger
import logging
logger = logging.getLogger('poretools')

# poretools imports
import poretools.version

def run_subtool(parser, args):
    import squiggle as submodule

    # run the chosen submodule.
    submodule.run(parser, args)

class ArgumentParserWithDefaults(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super(ArgumentParserWithDefaults, self).__init__(*args, **kwargs)
	self.add_argument("-q", "--quiet", help="Do not output warnings to stderr",
                        action="store_true",
                        dest="quiet")

def main():
    logging.basicConfig()

    #########################################
    # create the top-level parser
    #########################################
    parser = argparse.ArgumentParser(prog='poretools', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-v", "--version", help="Installed poretools version",
                        action="version",
                        version="%(prog)s " + str(poretools.version.__version__))
    subparsers = parser.add_subparsers(title='[sub-commands]', dest='command', parser_class=ArgumentParserWithDefaults)

    ###########
    # squiggle
    ###########
    parser_squiggle = subparsers.add_parser('squiggle',
                                        help='Plot the observed signals for FAST5 reads.')
    parser_squiggle.add_argument('files', metavar='FILES', nargs='+',
                             help='The input FAST5 files.')
    parser_squiggle.add_argument('--saveas',
                             dest='saveas',
                             metavar='STRING',
                             choices=['pdf', 'png'],
                             help='Save the squiggle plot to a file.',
                             default=None)
    parser_squiggle.add_argument('--num-facets',
                              dest='num_facets',
                              metavar='INTEGER',
                              default=6,
                              type=int,
                              help=('The number of plot facets (sub-plots). More is better for long reads. (def=6)'))
    parser_squiggle.add_argument('--theme-bw',
                             dest='theme_bw',
                             default=False,
                             action='store_true',
                             help="Use a black and white theme.")

    parser_squiggle.set_defaults(func=run_subtool)

    args = parser.parse_args()

    if args.quiet:
        logger.setLevel(logging.ERROR)

    try:
      args.func(parser, args)
    except IOError, e:
         if e.errno != 32:  # ignore SIGPIPE
             raise

if __name__ == "__main__":
    main()
