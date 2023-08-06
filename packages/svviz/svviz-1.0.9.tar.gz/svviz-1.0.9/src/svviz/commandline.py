import argparse
import logging
import sys
import tempfile

import svviz
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
        autoExport = ("--auto-export" in options)

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
            if autoExport:
                # put this as a global in demo module so that it persists until we
                # run the "open" command on the file
                demo.TEMPDIR = tempfile.mkdtemp()
                inputArgs.extend(["--export", "{}/temp.pdf".format(demo.TEMPDIR), "-O"])

            logging.info("Running the following command:")
            logging.info("{} {}".format(sys.argv[0], " ".join(inputArgs)))
            logging.info("")
        else:
            raise Exception("couldn't load demo command from info.txt file.")

    return inputArgs

def parseArgs(args):
    inputArgs = checkDemoMode(args)

    parser = argparse.ArgumentParser(usage="%(prog)s [options] [demo] [ref breakpoint...] [ref vcf]",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="Breakpoint formats:\n{}\n\nFor an example, run 'svviz demo'.".format(getBreakpointFormatsStr()))

    parser.add_argument("ref", help=
        "reference fasta file (a .faidx index file will be created if it doesn't exist so you need \n"
        "write permissions for this directory)")
    parser.add_argument("breakpoints", nargs="*", help=
        "information about the breakpoint to be analyzed; see below for information")

    requiredParams = parser.add_argument_group("required parameters")
    requiredParams.add_argument("-b", "--bam", action="append", help=
        "sorted, indexed bam file containing reads of interest to plot; can be specified multiple \n"
        "times to load multiple samples")

    inputParams = parser.add_argument_group("input parameters")
    inputParams.add_argument("-t", "--type", help=
        "event type: either del[etion], ins[ertion], mei (mobile element insertion), or batch (for \n"
        "reading variants from a VCF file in batch mode)")

    inputParams.add_argument("-A", "--annotations", action="append", help=
        "bed file containing annotations to plot; will be compressed and indexed using samtools \n"
        "tabix in place if needed (can specify multiple annotations files)")

    # Obsolete
    inputParams.add_argument("-o", "--orientation", help=argparse.SUPPRESS)

    inputParams.add_argument("--fasta", help=
        "An additional indexable fasta file specifying insertion sequences (eg mobile element \n"
        "sequences)")

    inputParams.add_argument("-q", "--min-mapq", metavar="MAPQ", default=0, type=float, help=
        "minimum mapping quality for reads")
    inputParams.add_argument("--pair-min-mapq", metavar="PAIR_MAPQ", default=0,
        type=float, help=
        "include only read pairs where at least one read end exceeds PAIR_MAPQ")
    inputParams.add_argument("-a", "--aln-quality", metavar="QUALITY", type=float, help=
        "minimum score of the Smith-Waterman alignment against the ref or alt allele in order to be \n"
        "considered (multiplied by 2)")
    inputParams.add_argument("--include-supplementary", action="store_true", help=
        "include supplementary alignments (ie, those with the 0x800 bit set in the bam flags); \n"
        "default: false")

    interfaceParams = parser.add_argument_group("interface parameters")
    interfaceParams.add_argument("-v", "--version", action="version", 
        version="svviz version {}".format(svviz.__version__), help=
        "show svviz version number and exit")
    interfaceParams.add_argument("--no-web", action="store_true", help=
        "don't show the web interface")
    interfaceParams.add_argument("--save-reads", metavar="OUT_BAM_PATH", help=
        "save relevant reads to this file (bam)")

    interfaceParams.add_argument("-e", "--export", metavar="EXPORT", type=str, help=
        "export view to file; in single variant-mode, the exported file format is determined from \n"
        "the filename extension unless --format is specified; in batch mode, this should be the name \n"
        "of a directory into which to save the files (use --format to set format); setting --export \n"
        "automatically sets --no-web")
    interfaceParams.add_argument("--format", type=str, help="file export format, either svg, png or \n"
        "pdf; by default, this is pdf (batch mode) or automatically identified from the file \n"
        "extension of --export")
    interfaceParams.add_argument("-O", "--open-exported", action="store_true", help=
        "automatically open the exported file")
    interfaceParams.add_argument("--thicker-lines", action="store_true", help=
        "Reads are shown with thicker lines, potentially overlapping one another, but increasing \n"
        "contrast when zoomed out")

    interfaceParams.add_argument("--dotplots", action="store_true", help=
        "generate dotplots to show sequence homology within the aligned region; requires some \n"
        "additional optional python libraries (scipy and PIL) and may take several minutes for \n"
        "longer variants")

    interfaceParams.add_argument("--summary", metavar="SUMMARY_FILE", help=
        "save summary statistics to this (tab-delimited) file")

    defaults = parser.add_argument_group("presets")
    defaults.add_argument("--pacbio", action="store_true", help=
        "sets defaults for pacbio libraries")

    if len(inputArgs)<1:
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
        if args.type!="batch" and not args.export.lower()[-3:] in ["svg", "png", "pdf"]:
            print "Export filename must end with one of .svg, .png or .pdf"
            sys.exit(1)

    logging.info(str(args))
    return args

if __name__ == '__main__':
    print parseArgs()