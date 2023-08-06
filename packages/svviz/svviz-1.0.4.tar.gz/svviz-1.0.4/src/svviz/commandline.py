import argparse
import logging
import sys

from svviz import demo
from svviz.alignment import AlignmentSet
from svviz.variants import getBreakpointFormatsStr

def setDefault(args, key, default):
    if args.__dict__[key] is None:
        args.__dict__[key] = default

def checkDemoMode(args):
    inputArgs = args[1:]

    if len(inputArgs) < 1:
        return []
    
    if inputArgs[0] == "test":
        inputArgs = "demo 1 -a --no-web".split(" ")

    if inputArgs[0] == "demo":
        options = [x for x in inputArgs if x.startswith("-")]
        inputArgs = [x for x in inputArgs if not x.startswith("-")]

        which = "example1"
        autoDownload = ("--auto-download" in options or "-a" in options)
        noweb = ("--no-web" in options or "-n" in options)

        if len(inputArgs) > 1:
            if inputArgs[1] in ["1","2"]:
                which = "example{}".format(inputArgs[1])
            else:
                raise Exception("Don't know how to load this example: {}".format(inputArgs[1]))
        cmd = demo.loadDemo(which, autoDownload)
        if cmd is not None:
            inputArgs = cmd
            if noweb:
                inputArgs.append("--no-web")
            logging.info("Running the following command:")
            logging.info("{} {}".format(sys.argv[0], " ".join(inputArgs)))
            logging.info("")
        else:
            raise Exception("couldn't load demo command from info.txt file.")

    return inputArgs

def parseArgs(args):
    inputArgs = checkDemoMode(args)

    parser = argparse.ArgumentParser(usage="%(prog)s [options] [demo] [ref breakpoint...]",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="Breakpoint formats:\n{}\n\nFor an example, run 'svviz demo'.".format(getBreakpointFormatsStr()))

    parser.add_argument("ref", help="reference fasta file (a .faidx index file will be \n"
        "created if it doesn't exist so you need write permissions for this directory)")
    parser.add_argument("breakpoints", nargs="*", help="information about the breakpoint to be analyzed; see below for information")

    requiredParams = parser.add_argument_group("required parameters")
    requiredParams.add_argument("-b", "--bam", action="append", help="sorted, indexed bam file containing reads of interest to plot; \n"
        "can be specified multiple times to load multiple samples")

    inputParams = parser.add_argument_group("input parameters")
    inputParams.add_argument("-t", "--type", help="event type: either del[etion], ins[ertion] or mei (mobile element insertion)")

    inputParams.add_argument("-A", "--annotations", action="append", help="bed file containing annotations to plot; will be compressed and indexed \n"
        "using samtools tabix in place if needed (can specify multiple annotations files)")

    inputParams.add_argument("-o", "--orientation", help=argparse.SUPPRESS)
    # inputParams.add_argument("-d", "--search-dist", metavar="DISTANCE", type=int, help="distance in base-pairs from the breakpoints to search for reads; \n"
        # "default: 2x the isize-mean (paired end) or 1000 (single-end)")

    inputParams.add_argument("-q", "--min-mapq", metavar="MAPQ", default=0, type=float, 
        help="minimum mapping quality for reads")
    inputParams.add_argument("--pair-min-mapq", metavar="PAIR_MAPQ", default=0,
        type=float, help="include only read pairs where at least one read end exceeds PAIR_MAPQ")
    inputParams.add_argument("-a", "--aln-quality", metavar="QUALITY", type=float, 
        help="minimum score of the Smith-Waterman alignment against the ref or alt allele \nin order to be considered (multiplied by 2)")
    inputParams.add_argument("--include-supplementary", action="store_true", help="include supplementary alignments "
        "(ie, those with the 0x800 bit set in the bam flags); \ndefault: false")

    interfaceParams = parser.add_argument_group("interface parameters")
    interfaceParams.add_argument("--no-web", action="store_true", help="don't show the web interface")
    interfaceParams.add_argument("--save-reads", metavar="OUT_BAM_PATH", help="save relevant reads to this file (bam)")
    inputParams.add_argument("-e", "--export", metavar="EXPORT", type=str, help="export view to file; exported file format is determined \n"
        "from the filename extension (automatically sets --no-web)")
    inputParams.add_argument("-O", "--open-exported", action="store_true", help="automatically open the exported file")

    defaults = parser.add_argument_group("presets")
    defaults.add_argument("--pacbio", action="store_true", help="sets defaults for pacbio libraries")

    if len(inputArgs)<=1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args(inputArgs)
    args._parser = parser

    if args.pacbio:
        # TODO: should infer this from the input if possible, per-sample
        setDefault(args, "aln_quality", 0.65)


    if args.aln_quality is not None:
        AlignmentSet.AlnThreshold = args.aln_quality
    
    if args.export is not None:
        args.no_web = True
        if not args.export.lower()[-3:] in ["svg", "png", "pdf"]:
            print "Export filename must end with one of .svg, .png or .pdf"
            sys.exit(1)

    logging.info(str(args))
    return args

if __name__ == '__main__':
    print parseArgs()