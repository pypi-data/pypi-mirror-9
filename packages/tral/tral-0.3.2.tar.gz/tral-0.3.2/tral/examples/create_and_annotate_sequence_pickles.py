import argparse
from collections import defaultdict
import csv
import logging
import logging.config
import os
import pickle
from Bio import SeqIO
from pyfaidx import Fasta

from tral.paths import *
from tral.sequence import sequence


logging.config.fileConfig(config_file("logging.ini"))
log = logging.getLogger('root')

PFAM_deleted = ['PF11206', 'PF13666']
PFAM_replaced = {'PF11930': 'PF00501', 'PF08959': 'PF04969'}

def split_pfam_annotations(annotation_file, sequence_dir, results_dir):

    with open(annotation_file, 'rb') as fh:
        p = pickle.load(fh)

    lFiles = [i for i in os.listdir(sequence_dir) if not i.endswith("fai")]
    for iFile in lFiles:
        lSequence = Fasta(os.path.join(sequence_dir, iFile))

        dP = {i:p[i[3:9]] for i in lSequence.keys() if i[3:9] in p}

        # Replace or remove outdated PFAM annotations
        dP = {i:[k if not k in PFAM_replaced else PFAM_replaced[k] for k in j if not k in PFAM_deleted] for i,j in dP.items()}

        results_file = os.path.join(results_dir, iFile + "_PFAM.pickle")
        with open(results_file, "wb") as fh2:
            pickle.dump(dP, fh2)

def read_pfam_uniprot(annotation_data_file, output_file):
    ''' annotation_file from:
        http://www.uniprot.org/uniprot/?query=database:(type:pfam%20AND%20*)&fil=&sort=score '''

    p = {}
    if annotation_data_file:
        try:
            with open(annotation_data_file) as f:
                reader = csv.reader(f, delimiter="\t")
                for row in reader:
                    p[row[0]] = row[1][:-1].split(";")
        except:
            raise Exception("Cannot load sequence annotation file annotation_data_file: {}".format(annotation_data_file))

    with open(output_file, 'wb') as fh:
       pickle.dump(p,fh)


def annotate_seq_pickles(sequence_dir, results_dir, annotation_pickle):

    with open(annotation_pickle, 'rb') as fh:
        annotations = pickle.load(fh)

    for file in os.listdir(sequence_dir):
        if file.endswith(".pickle"):
            with open(os.path.join(sequence_dir, file), 'rb') as fh:
                lSeq = pickle.load(fh)

            for iS in lSeq:
                if iS.id in annotations.keys():
                    iS.annotate(annotations[iS.id], "PFAM")

            output_file = os.path.join(results_dir, file)
            with open(output_file, 'wb') as fh:
                pickle.dump(lSeq, fh)

    print("DONE")


def create_and_annotate_seq_pickles(sequence_dir, results_dir, annotation_file = None, lFiles = None):

    ''' Create ``Sequence`` instances from fasta files and annotate with data.

    Create ``Sequence`` instances from fasta files and annotate with data.

    Args:
         sequence_dir (str): Path to the dir containing *.fasta sequence files.
         results_dir (str): Path to directory where the output files are saved.
         annotation_file (str): Path to a tab separated file with annotations to the
            sequences.

    Raises:
        Exception: If the pickle ``annotation_file`` cannot be loaded.
    '''

    if annotation_file:
        try:
            with open(annotation_file, 'rb') as fh:
                annotations = pickle.load(fh)
        except:
            raise Exception("Cannot load sequence annotation file annotation_file: {}".format(annotation_file))

    if not lFiles:
        lFiles = list(os.listdir(sequence_dir))
        lFiles = [file for file in lFiles if file.endswith(".fasta")]

    for file in lFiles:
        lSeq = sequence.Sequence.create(file = os.path.join(sequence_dir, file), format = 'fasta')

        if annotation_file:
            for iS in lSeq:
                # The fasta files sequence ID follow the pattern "sp|SPID|SPNAME"
                # Here, we extract SPID
                iS.id_long = iS.id
                iS.id = iS.id.split("|")[1]
                if iS.id in annotations.keys():
                    print(annotations[iS.id])
                    iS.annotate(annotations[iS.id], "PFAM")

        output_file = os.path.join(results_dir, file.replace("fasta", "pickle"))
        with open(output_file, 'wb') as fh:
            pickle.dump(lSeq, fh)

    print("DONE")


def main():

    pars = read_commandline_arguments()

    kwargs = {"sequence_dir": pars["input"], "results_dir": pars["results_dir"]}

    if "annotation_file" in pars:
        kwargs["annotation_file"] = pars["annotation_file"]
    if "file_list" in pars:
        kwargs["lFiles"] = pars["file_list"]


    if pars["method"] == "create_and_annotate_seq_pickles":
        create_and_annotate_seq_pickles(**kwargs)
    elif pars["method"] == "split_pfam_annotations":
        split_pfam_annotations(**kwargs)



def read_commandline_arguments():

    parser = argparse.ArgumentParser(description='Process create hmm pickles options')
    parser.add_argument('method', metavar='method_name', type=str,
                       help='The name of the method to be executed.')
    parser.add_argument('-i','--input', type=str, required=True,
                       help='The path to the sequence directory containing .fasta files, e.g. /path/to/sequence_dir')
    parser.add_argument('-o','--results_dir', type=str, required=True,
                       help='The path to the output files, e.g. /path/to/output')
    parser.add_argument('-a', '--annotation_file', type=str,
                       help='The path to the annotation data tab-separated file.')
    parser.add_argument('-f', '--file_list', type=str, nargs='+',
                       help='A list of files to work on.')

    pars = vars(parser.parse_args())
    pars = {key: value for key, value in pars.items() if value != None}
    return pars


if __name__ == "__main__":
    main()
