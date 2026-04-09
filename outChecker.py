import os
import subprocess
input_file = ""
input_dir = "inputs" # folder containing the output.txt files for verification
output_dir = "outputs" # folder for containing the output.txt files
verified_output_dir = "VerifiedOutputs"
os.makedirs(output_dir, exist_ok=True)
os.makedirs(verified_output_dir, exist_ok=True)

for filename in os.listdir(output_dir):
    if not filename.endswith(".txt"):
        continue

    # extract the group number
    output_path = os.path.join(output_dir, filename)
    if filename.startswith("output"):
        group_number = filename.replace("output_group", "").replace(".txt", "")
        verified_output_path = os.path.join(verified_output_dir, f"{group_number}GRAPHSOLVER.txt")
    else:
        group_number = filename.replace("LARGE", "").replace(".txt", "")
        verified_output_path = os.path.join(verified_output_dir, f"{group_number}SA.txt")
    
    for file in os.listdir(input_dir):
        inputGroup = file.replace("input_group", "").replace(".txt", "")
        if inputGroup == group_number:
            input_file = input_dir + "/" + file
    
    print(f"Running verification on {output_path}...")

    with open(verified_output_path, "w") as voutfile:
        result = subprocess.run(["python3", "verification.py", "-fin", input_file, "-fout", output_path], stdout = voutfile, stderr=subprocess.PIPE)
    
    if result.returncode != 0:
        print(f"  ERROR on {filename}: {result.stderr.decode()}")
    else:
        print(f"  Done -> {output_path}")
