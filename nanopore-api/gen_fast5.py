from Bio import SeqIO
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider


def generate_signal(pore_model, kmer_list, draw):
    signal = []
    model = pd.read_csv(pore_model, sep='\t', header=0)
    model = model.set_index("kmer", drop= False)

    if draw == 0:
        for x, _ in kmer_list:
            signal.append(model.loc[x, "level_mean"])
    else:
        for x, y in kmer_list:
            row = model.loc[x, "level_mean":"level_stdv"]
            signal.append(np.random.normal(row[0], row[1]))
    return signal


def kmer_count_and_list(fasta_file, k):
    kmer_count = {}
    kmer_list = []
    fasta = SeqIO.read(fasta_file, "fasta")
    dna = fasta.seq

    for x in range(len(dna)+1-k):
        # kmer = dna[x:x+k]
        kmer = dna[x:x+k]
        kmer_list.append((str(kmer), 0.0))
        kmer_count[kmer] = kmer_count.get(kmer, 0) + 1
    return kmer_count, kmer_list


# def gen_data_struct(signals):
#     for signal in signals:



def plot_signal(signal_1, signal_2):
    fig, ax = plt.subplots(figsize=(60,30))
    plt.subplots_adjust(bottom=0.25)

    plt.plot(signal_1)
    plt.plot(signal_2)

    plt.show()


fasta_file = 'artificial/sequence1.fasta'
fasta_file2 = 'artificial/sequence2.fasta'
k = 6
_, kmer_list1 = kmer_count_and_list(fasta_file, k)
_, kmer_list2 = kmer_count_and_list(fasta_file2, k)
pore_model = 'kmer_models/r9.4_180mv_450bps_6mer/template_median68pA.model'
a = generate_signal(pore_model, kmer_list1, 0)
b = generate_signal(pore_model, kmer_list2, 0)
print(a)
# plot_signal(a, b)
