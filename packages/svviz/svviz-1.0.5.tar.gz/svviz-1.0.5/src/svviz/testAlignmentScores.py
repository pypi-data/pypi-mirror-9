import re
import sys
import numpy
import pysam
from ssw import ssw_wrap
from svviz.alignment import _getBlastRepresentation
import pyfaidx

from biorpy import r, plotting


def rescore(read_seq, genome_seq, cigar,
    match=2, mismatch=1, gap_open=2, gap_extend=0):

    pattern = re.compile('([0-9]*)([MIDNSHP=X])')

    genomepos = 0
    seqpos = 0

    score = 0

    matches = 0
    mismatches = 0
    insertions = 0
    deletions = 0
    extensions = 0

    for length, code in pattern.findall(cigar):
        length = int(length)

        if code == "M":
            for i in range(length):
                g = genome_seq[genomepos]
                s = read_seq[seqpos]

                if g == s:
                    score += match
                    matches += 1
                else:
                    mismatches += 1
                    score -= mismatch

                genomepos += 1
                seqpos += 1
        elif code in "D":
            score -= gap_open
            deletions += 1
            for i in range(length):
                extensions += 1
                score -= gap_extend
                g = genome_seq[genomepos]
                genomepos += 1
        elif code in "IHS":
            insertions += 1
            score -= gap_open
            for i in range(length):
                extensions += 1
                score -= gap_extend
                seqpos += 1
    return score, matches, mismatches, insertions, deletions, extensions

    r"([0-9]+([A-Z]|\^[A-Z]+)[0-9]+)*"

bam = pysam.Samfile(sys.argv[1], "rb")
ref = pyfaidx.Fasta(sys.argv[2], as_raw=True)

chr1 = "chr1" if "chr1" in bam.references else "1"

# scores = []
# nms = []
# indels = []
# indels2 = []
# ass = []
# lengths = []
# mms = []

lengths = []
mismatches = []
indels = []
insertions = []
deletions = []

badbegin = 0
badend = 0
badboth = 0

badscore = 0

good = 0

corrected = []


for i, read in enumerate(bam.fetch(chr1, 1000000)):
    if read.is_unmapped:
        continue
    hardclipped = 0
    for op, l in read.cigartuples:
        if op == 5:
            hardclipped += l
    if hardclipped < 5:
        print read

    good += 1
    curref = ref[chr1][read.reference_start-100:read.reference_end+100].upper()
    curseq = read.seq

    # nms.append(read.opt("NM"))#/float(len(read.seq)))
    # ass.append(read.opt("AS"))#/float(len(read.seq)))
    # indels.append(sum(1 for i in zip(*read.cigartuples)[1] if i in[1,2]))#/float(len(read.seq)))

    aligner = ssw_wrap.Aligner(curref, report_cigar=True)#,
        # match=1,
        # mismatch=4,
        # gap_open=6,
        # gap_extend=1
        # )
    aln = aligner.align(curseq)

    if aln.score / 2.0 < len(read.seq) * 0.65:
        badscore += 1
    # scores.append(aln.score)
    # lengths.append(len(read.seq))

    # indels2.append(aln.cigar_string.count("I")+aln.cigar_string.count("D"))

    score, curmatches, curmismatches, curinsertions, curdeletions, curextensions = rescore(curseq, curref[aln.ref_begin:aln.ref_end+1], aln.cigar_string)
    curindels = sum(1 for i in zip(*read.cigartuples)[1] if i in[1,2])

    lengths.append(len(read.seq))
    mismatches.append(curmismatches)
    indels.append(curindels)

    insertions.append(sum(1 for i in zip(*read.cigartuples)[1] if i in[1]))
    deletions.append(sum(1 for i in zip(*read.cigartuples)[1] if i in[2]))

    curcorrected = aln.score / 2.0 / len(read.seq)
    corrected.append(curcorrected)
    if curcorrected > 0.95:
        print read

    # if curinsertions + curdeletions + curmismatches < 5:
    if aln.query_begin > len(read.seq)*0.1:
        if aln.query_end < len(read.seq)*0.9:
            badboth += 1
        else:    
            badbegin += 1
    elif aln.query_end < len(read.seq)*0.9:
        badend += 1
        # print ""
        # print aln.query_begin, aln.query_end, len(read.seq), aln.cigar_string
        # print curinsertions, curdeletions, curmismatches
        # blastStrings = _getBlastRepresentation(curseq, curref[aln.ref_begin:aln.ref_end+1], aln.cigar_string).split("\n")
        # for bs in blastStrings:
        #     print bs[:200]
    # print score, matches*1-mismatches*4-(insertions+deletions)*6-extensions*1, len(read.seq)-read.opt("NM")*5-curindels*6-extensions

    # mms.append(mismatches)
    #, insertions+deletions, sum(1 for i in zip(*read.cigartuples)[1] if i in[1,2])
    #, aln.score, read.opt("NM"), read.opt("AS")
    # print re.findall('([0-9]*)([MIDNSHP=X])', aln.cigar_string)
    # blastStrings = _getBlastRepresentation(curseq, curref[aln.ref_begin:aln.ref_end+1], aln.cigar_string).split("\n")
    # for bs in blastStrings:
    #     print bs[:100]


    # # print read.opt("NM"), len(read.cigartuples), len(aln.cigar_string)
    # print ""

    if i > 1000:
        print "DONE:", i
        break

print "bad begin:", badbegin
print "bad end:", badend
print "bad both:", badboth

print "bad score:", badscore
print "good:", good

r.par(mfcol=[2,2])

# r.hist(mismatches, main="mismatches")
# r.hist(indels, main="indels")

r.hist([mismatches[i]/float(lengths[i]) for i in range(len(mismatches))], main="mismatches (norm)", breaks=40)
r.hist([indels[i]/float(lengths[i]) for i in range(len(mismatches))], main="indels (norm)", breaks=40)
r.hist([insertions[i]/float(lengths[i]) for i in range(len(mismatches))], main="insertions (norm)", breaks=40)
# r.hist([deletions[i]/float(lengths[i]) for i in range(len(mismatches))], main="deletions (norm)", breaks=40)

r.hist(corrected, main="corrected", breaks=40)


# plotting.plotWithCor(mms, [nm/4.0 for nm in nms], main="NM vs mismatches")
# r.abline(a=0, b=1, col="red")


# plotting.plotWithCor(scores, nms, main="NM")
# r.abline(a=0, b=1, col="red")
# # plotting.plotWithCor(scores, indels, main="INDELs")
# # r.abline(a=0, b=1, col="red")
# # plotting.plotWithCor(scores, ass, main="ASs")
# # r.abline(a=0, b=1, col="red")

# # plotting.plotWithCor(scores, indels, main="indels1")
# # r.abline(a=0, b=1, col="red")
# # plotting.plotWithCor(scores, indels2, main="indels2")
# # r.abline(a=0, b=1, col="red")

# plotting.plotWithCor(indels, indels2, main="indels vs indels")
# r.abline(a=0, b=1, col="red")

# # plotting.plotWithCor(scores, lengths, main="lengths")
# # r.abline(a=0, b=1, col="red")
# # plotting.plotWithCor(scores, 2*numpy.array(indels)+numpy.array(nms), main="SUM")
# # r.abline(a=0, b=1, col="red")

raw_input("")