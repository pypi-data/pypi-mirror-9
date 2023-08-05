import argparse
import sys
import re

class FastaParser(object):
    """docstring for FastaParser"""
    def __init__(self, infile):
        super(FastaParser, self).__init__()
        self.infile = infile

        #gaps
        self.nr_gaps = 0
        self.tot_gap_length = 0
        self.gap_distr = []

        #sequence
        self.contig_lengths = []

    def __str__(self):
        #print 'nr_gaps\ttot_gap_length'
        print 'nr_gaps: {0}\ntot_gap_length: {1} \n Avg. gap length: {2} \n Longest gap:{3}'.format(self.nr_gaps,self.tot_gap_length, self.tot_gap_length/self.nr_gaps, max(self.gap_distr))
        for i,n in enumerate(self.NX_stats):
            print 'N{0}0: {1}'.format(i+1,n)
        print 'tot assembly length:{0}'.format(self.tot_assembly_length)
        return
    def get_stats(self):
        j = 0
        for acc, seq in fasta_iter(self.infile):
            j+=1
            if j==10000:
                print 'reading {0} contigs'.format(j)
            self.calc_gaps(seq)
            self.add_contig_length(seq)

        self.N_stats = []
        for i in range(10,99,10):
            print i
            self.NX_stats.append(self.NX(i, self.contig_lengths))

    def calc_gaps(self, seq):
        gap_list = re.findall('[Nn]+', seq)
        gap_lengths = map(lambda x: len(x), gap_list)
        self.gap_distr += gap_lengths
        self.tot_gap_length += sum(gap_lengths)
        self.nr_gaps += len(gap_lengths)

    def add_contig_length(self, seq):
        self.contig_lengths.append(len(seq))

    def NX(self,x,lengths):
        lengths.sort(reverse=True)
        tot_length = sum(lengths)
        self.tot_assembly_length = tot_length
        stop = tot_length/ (100/float(x))
        curr_sum = 0
        for length in lengths:
            curr_sum += length
            if curr_sum >= stop:
                return length


def fasta_iter(fasta_file):
    """
        Reads a fasta file into memory.

        Arguments:
        fasta_file - A python file object. The file should be in 
        fasta format.

        Returns:
            an iterator over accession, sequence.

    """  

    k = 0
    temp = []
    accession = ''
    for line in fasta_file:
        if line[0] == '>' and k == 0:
            accession = line[1:].strip().split()[0]
            k += 1
        elif line[0] == '>':
            temp = ''.join(temp)
            yield accession, temp
            temp = []
            accession = line[1:].strip().split()[0]
        else:
            temp.append(line.strip())
    
    temp = ''.join(temp)
    yield accession, temp


def main(args):
    try:
        infile = open(args.infile,'r')
    except IOError:
        sys.stderr.write('{0} does not exist. skipping...\n'.format(args.infile))
        print '{0},{1}'.format('-','-')
        sys.exit()

    c = FastaParser(infile)
    c.get_stats()

    print c



if __name__ == '__main__':
    ##
    # Take care of input
    parser = argparse.ArgumentParser(description="Calculate number of gaps and total number of N's in a scaffold.fasta file")
    parser.add_argument('infile',type=str, help='A contig/scaffol fasta file.')
    args = parser.parse_args()
    main(args)