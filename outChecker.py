import os
import subprocess
import shutil

input_dir = "inputs" # folder containing the output.txt files for verification
output_dir = "outputs" # folder for containing the output.txt files
verified_output_dir = "VerifiedOutputs"
os.makedirs(output_dir, exist_ok=True)
os.makedirs(verified_output_dir, exist_ok=True)

for filename in os.listdir(output_dir):
    print()
    if not filename.endswith(".txt"):
        continue

    # extract the group number
    output_path = os.path.join(output_dir, filename)
    group_number = filename.replace("LARGE", "").replace("output_group", "").replace("SMALL", "").replace("_manual", "").replace(".txt", "")

    input_file = ""
    for file in os.listdir(input_dir):
        inputGroup = file.replace("input_group", "").replace(".txt", "")
        if inputGroup == group_number:
            input_file = input_dir + "/" + file

    print(f"Running verification on {output_path}...")

    result = subprocess.run(["python3", "verification.py", "-fin", input_file, "-fout", output_path], stderr=subprocess.PIPE)

    if result.returncode == 3:
        print(f"  Bad Input Error on {input_file}: {result.stderr.decode()}")
    elif result.returncode == 2:
        print(f"  Verification failed on {filename}: {result.stderr.decode()}")
    elif result.returncode != 0:
        print(f"  Error on {filename}: {result.stderr.decode()}")
    else:
        print(f"  Output Verified: {output_path}")
        verified_output_path = ""
        for file in os.listdir(verified_output_dir):
            if group_number in file:
                verified_output_path = verified_output_dir + "/" + file
        if verified_output_path:
            with open(verified_output_path, "r", encoding="utf-8") as best_soln:
                best_score = int(best_soln.readline().replace("\n", ""))
            with open(output_path, "r", encoding="utf-8") as new_soln:
                new_score = int(new_soln.readline().replace("\n", ""))
            if new_score <= best_score:
                continue
            print(f"Improvements: {best_score} -> {new_score}")
        else:
            verified_output_path = f"{verified_output_dir}/{group_number}.txt"
            # copy new output to verified output path
        shutil.copyfile(output_path, verified_output_path)
        print(f"  Optimal Output Found -> {verified_output_path}")
