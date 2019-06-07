import pysam as sam
import sys
import json
import os


def get_pos(file_path, name):
    bamfile = sam.AlignmentFile(file_path, "rb")
    idx = sam.IndexedReads(bamfile)
    idx.build()
    name = idx.find(name)

    #finds first
    for read in name:
        pos = read.reference_start
        break

    bamfile.close()

    return pos


def get_cigar(file_path, name):
    bamfile = sam.AlignmentFile(file_path, "rb")
    idx = sam.IndexedReads(bamfile)
    idx.build()
    name = idx.find(name)

    cigar_align = []

    for read in name:
        # tmp = read.get_blocks()
        if (not (read.is_unmapped)):  # if it's mapped
            cigarLine = read.cigar

            for (cigarType, cigarLength) in cigarLine:
                try:
                    if (cigarType == 0):  # match
                        for i in range(cigarLength):
                            cigar_align.append('.')
                    elif (cigarType == 1):  # insertions
                        for i in range(cigarLength):
                            cigar_align.append('i')
                    elif (cigarType == 2):  # deletion
                        for i in range(cigarLength):
                            cigar_align.append('d')
                    elif (cigarType == 3):  # skip
                        for i in range(cigarLength):
                            cigar_align.append('s')
                    elif (cigarType == 4):  # soft clipping
                        continue
                    elif (cigarType == 5):  # hard clipping
                        continue
                    elif (cigarType == 6):  # padding
                        for i in range(cigarLength):
                            cigar_align.append('p')
                    else:
                        print("Wrong CIGAR number")
                        sys.exit(1)
                except:
                    print("Problem")
        return cigar_align
