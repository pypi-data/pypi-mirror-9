import multiprocessing
from ssw import ssw_wrap

ref = "AGTGCTGCTGTCGTGAGACTGCTGCTG"

def align(seq):
    # print seq
    aligner = ssw_wrap.Aligner(ref)
    aligner.align(seq)
    return seq

def main():
    seqs = ["AGCGGAGCTTCG", "ACCCAACCA", "TTTTTTAGGA", "CCCCCCGT", "AGGAGNNNNNNNNNN", "GATGTTATAT", "NNNNNNNGTATAGA"]

    pool = multiprocessing.Pool(processes=1)
    result = pool.map(align, seqs)

    pool.close()
    pool.join()

if __name__ == '__main__':
    for i in range(1000):
        main()
