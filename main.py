import argparse
import os
import time
from pathlib import Path

import torch
from pandas import DataFrame

from BacteriocinClassifier import BacteriocinClassifier
from ELMo import encode_input_fasta


def main(cuda_device, fasta_input_file, csv_output_file, fasta_input_paste=False):
    if cuda_device is None:
        cuda_device = 0 if torch.cuda.is_available() else -1
        print(f'No cuda device specified. Using cuda device {cuda_device}')

    if fasta_input_file is None and not fasta_input_paste:
        fasta_input_file = "./test_data/sample_fasta.faa"
        print(f"No input fasta file specified. Using {fasta_input_file}")

    elif fasta_input_paste:
        fasta_input_file = "temp_fasta.faa"
        fasta_paste = input("Paste fasta file:\n")
        with open(fasta_input_file, 'w') as f:
            f.write(fasta_paste)

    if csv_output_file is None:
        csv_output_file = "./results.csv"
        print(f"No output path specified. Using {csv_output_file}")

    inpt, inpt_names = encode_input_fasta(input_fasta=Path(fasta_input_file),
                                          cuda_device=cuda_device)

    os.remove("temp_fasta.faa") if fasta_input_paste else None

    net: BacteriocinClassifier = BacteriocinClassifier()
    net.load_state_dict(torch.load("./weights/bacteriocin_classifier_params.dump"))
    net.eval()

    print("Predicting sequences..")
    start_time = time.time()
    outpt = net(inpt)
    end_time = time.time()
    print(f"Took {end_time - start_time} seconds")

    # Save results
    out_df = DataFrame(outpt.detach().numpy(),
                       columns=['not_bacteriocin_score', 'bacteriocin_score'])
    out_df['Name'] = inpt_names
    out_df[['Name', 'not_bacteriocin_score', 'bacteriocin_score']].to_csv(csv_output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--cuda_device", help='Specify which cuda device to use', type=int)
    parser.add_argument("-f", "--fasta_input_file",
                        help='Input fasta file with sequences to classify', type=str)
    parser.add_argument("-o", "--csv_output_file", help='Where to output csv file with results',
                        type=str)
    parser.add_argument("-p", "--fasta_input_paste",
                        help='Flag to get input fasta from pasting into terminal',
                        action="store_true")
    parser.add_argument("--mode", help='not used')
    parser.add_argument("--port", help='not used')
    args = parser.parse_args()

    main(cuda_device=args.cuda_device, fasta_input_file=args.fasta_input_file,
         csv_output_file=args.csv_output_file, fasta_input_paste=args.fasta_input_paste)
