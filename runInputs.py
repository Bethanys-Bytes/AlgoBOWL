import os
import subprocess

input_dir = "inputs" # folder containing the input.txt files
output_dir = "outputs" # folder for containing the output.txt files

os.makedirs(output_dir, exist_ok=True)

for filename in os.listdir(input_dir):
    if not filename.endswith(".txt"):
        continue

    # extract the group number
    group_number = filename.replace("input_group", "").replace(".txt", "")

    input_path = os.path.join(input_dir, filename)
    output_path = os.path.join(output_dir, f"{group_number}SMALL.txt")

    print(f"Running solver on {filename}...")

    with open(input_path, "r") as infile, open(output_path, "w") as outfile:
        result = subprocess.run(["python3", "solverSmall.py"], stdin=infile, stdout = outfile, stderr=subprocess.PIPE)
    
    if result.returncode != 0:
        print(f"  ERROR on {filename}: {result.stderr.decode()}")
    else:
        print(f"  Done -> {output_path}")

"""
for filename in os.listdir(input_dir):
    if not filename.endswith(".txt"):
        continue

    # extract the group number
    group_number = filename.replace("input_group", "").replace(".txt", "")

    input_path = os.path.join(input_dir, filename)
    output_path = os.path.join(output_dir, f"{group_number}GRAPHSOLVER.txt")

    print(f"Running solver on {filename}...")

    with open(input_path, "r") as infile, open(output_path, "w") as outfile:
        result = subprocess.run(["python3", "graph_solver.py"], stdin=infile, stdout = outfile, stderr=subprocess.PIPE)
    
    if result.returncode != 0:
        print(f"  ERROR on {filename}: {result.stderr.decode()}")
    else:
        print(f"  Done -> {output_path}")
"""