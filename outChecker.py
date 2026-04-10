import os
import subprocess
import shutil
from argparse import ArgumentParser
import re

input_dir = "inputs" # folder containing the output.txt files for verification

parser = ArgumentParser()
parser.add_argument('-fout', '--output_dir', default="outputs") # folder for containing the output.txt files
parser.add_argument('-fopt', '--optimal_dir', default=None)
parser.add_argument('-o', '--verification_results', default=None)
args = parser.parse_args()

# verified_output_dir = "VerifiedOutputs"
os.makedirs(args.output_dir, exist_ok=True)
if args.optimal_dir:
    os.makedirs(args.optimal_dir, exist_ok=True)

def verify_directory(record_function):
    for filename in os.listdir(args.output_dir):
        record_function()
        if not filename.endswith(".txt"):
            continue

        # extract the group number
        output_path = os.path.join(args.output_dir, filename)
        group_number = ""
        for group_number_match in re.findall(r"\d+", filename):
            group_number = group_number_match

        if not group_number:
            record_function(f"No Group Number found: {output_path}")
            continue

        input_file = ""
        for file in os.listdir(input_dir):
            inputGroup = file.replace("input_group", "").replace(".txt", "")
            if inputGroup == group_number:
                input_file = input_dir + "/" + file

        record_function(f"Running verification on {output_path}...")

        result = subprocess.run(["python3", "verification.py", "-fin", input_file, "-fout", output_path], stderr=subprocess.PIPE)

        if result.returncode == 3:
            record_function(f"  Bad Input Error on {input_file}: {result.stderr.decode()}")
        elif result.returncode == 2:
            record_function(f"  Verification failed on {filename}: {result.stderr.decode()}")
        elif result.returncode != 0:
            record_function(f"  Error on {filename}: {result.stderr.decode()}")
        else:
            record_function(f"  Output Verified: {output_path}")
            if not args.optimal_dir:
                continue
            verified_output_path = ""
            for file in os.listdir(args.optimal_dir):
                if group_number in file:
                    verified_output_path = args.optimal_dir + "/" + file
            if verified_output_path:
                with open(verified_output_path, "r", encoding="utf-8") as best_soln:
                    best_score = int(best_soln.readline().replace("\n", ""))
                with open(output_path, "r", encoding="utf-8") as new_soln:
                    new_score = int(new_soln.readline().replace("\n", ""))
                if new_score <= best_score:
                    continue
                record_function(f"Improvements: {best_score} -> {new_score}")
            else:
                verified_output_path = f"{args.optimal_dir}/{group_number}.txt"
                # copy new output to verified output path
            shutil.copyfile(output_path, verified_output_path)
            record_function(f"  Optimal Output Found -> {verified_output_path}")

if args.verification_results:
    with open(args.verification_results, "w", encoding="utf-8") as f:
        def record_function(line=""):
            f.write(line + "\n")
            print(line)
        verify_directory(record_function)
else:
    verify_directory(lambda line = "": print(line))
