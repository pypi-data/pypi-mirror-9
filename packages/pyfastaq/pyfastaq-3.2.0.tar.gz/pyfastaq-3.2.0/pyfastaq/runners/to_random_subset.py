import argparse
import sys
import random
from pyfastaq import sequences, utils

def run(description):
    parser = argparse.ArgumentParser(
        description = 'Takes a random subset of reads from a sequence file and optionally the corresponding read ' +
                      'from a mates file.  Ouptut is interleaved if mates file given',
        usage = 'fastaq to_random_subset [options] <infile> <outfile> <percent>')
    parser.add_argument('--mate_file', help='Name of mates file')
    parser.add_argument('infile', help='Name of input file')
    parser.add_argument('outfile', help='Name of output file')
    parser.add_argument('percent', type=int, help='Per cent probability of keeping any given read (pair) in [0,100]', metavar='INT')
    options = parser.parse_args()

    seq_reader = sequences.file_reader(options.infile)
    fout = utils.open_file_write(options.outfile)

    if options.mate_file:
        mate_seq_reader = sequences.file_reader(options.mate_file)

    for seq in seq_reader:
        if options.mate_file:
            try:
                mate_seq = next(mate_seq_reader)
            except StopIteration:
                print('Error! Didn\'t get mate for read', seq.id, file=sys.stderr)
                sys.exit(1)
        if random.randint(0, 100) <= options.percent:
            print(seq, file=fout)
            if options.mate_file:
                print(mate_seq, file=fout)

    utils.close(fout)
