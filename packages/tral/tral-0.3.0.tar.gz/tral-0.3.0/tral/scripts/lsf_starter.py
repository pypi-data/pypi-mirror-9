import os
import sys
import itertools

from tral.paths import *

# gene_tree_dir = os.path.join(RESULTROOT,"Plants","1_TR_detected")
# lFile = [iF for iF in os.listdir(tr_dir) if iF.endswith(".pickle")]
# lTR_ID = [iFile.split(".")[0] for iFile in lFile]


def starter():

    command_file = "tandemrepeats/scripts/detect_tandem_repeats_in_sequence.py"
    job_name = "HHrepID"
    log_name = "HHrepID"

    run_time = 60
    param =

    memory = '-R "rusage[mem=12000]"'
    for jobID in lTR_ID:
        param = jobID + "+PFAM"
        myC = 'bsub -J {} -W {} {} -o {}_{}.log python {} {}'.format(job_name, run_time, memory, log_name, jobID, command_file, param)
        #print(myC)
        # (run script with -B -N flags) # B: Begin, N: End - sends me an email!
        os.system(myC)

    #parameters = ...


if __name__=="__main__":

    starter()

