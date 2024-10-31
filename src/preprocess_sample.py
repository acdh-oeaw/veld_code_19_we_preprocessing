import math
import os
import random
import subprocess
from datetime import datetime

import yaml


IN_FILE_PATH = "/veld/input/" + os.getenv("in_file")
OUT_FILE_PATH = "/veld/output/" + os.getenv("out_file")
OUT_DATA_DESCRIPTION = os.getenv("out_data_description")
OUT_LOG_PATH = "/veld/output/log.txt"
OUT_VELD_DATA_YAML_PATH = "/veld/output/veld_data_sampled.yaml"
TMP_FILE_FOLDER = "/tmp"
SAMPLE_RANDOM_SEED = os.getenv("sample_random_seed")
PERCENTAGE_SAMPLE = float(os.getenv("percentage_sample"))
BUFFER_SEGMENTS = int(os.getenv("buffer_segments"))


def get_line_indices():
    print("counting lines")
    line_indices_list = []
    with open(IN_FILE_PATH, "r") as f_in:
        for i, line in enumerate(f_in):
            line_indices_list.append(i)
        print(f"total_line_count: {len(line_indices_list)}")
    print("creating index list of random sample lines")
    absolute_sample = int((len(line_indices_list) / 100) * PERCENTAGE_SAMPLE)
    if SAMPLE_RANDOM_SEED is not None:
        random.seed(SAMPLE_RANDOM_SEED)
    rand_indices = sorted(random.sample(line_indices_list, absolute_sample))
    print(f"number of randomly sampled lines: {len(rand_indices)}")
    return set(rand_indices)


def create_sample(rand_indices_set):
    count_to_pick = len(rand_indices_set)
    count_picked = 0
    buffer_out_str = ""
    buffer_segment_step = math.ceil(count_to_pick / BUFFER_SEGMENTS)
    with open(IN_FILE_PATH, "r") as f_in:
        with open(OUT_FILE_PATH, "w") as f_out:
            for line_count, line in enumerate(f_in):
                if line_count in rand_indices_set:
                    rand_indices_set.remove(line_count)
                    count_picked += 1
                    buffer_out_str += line
                if (
                    line_count != 0
                    and (
                        line_count % buffer_segment_step == 0 
                        or count_picked == count_to_pick
                    )
                ):
                    f_out.write(buffer_out_str)
                    buffer_out_str = ""
                    print(f"picked {count_picked} lines, out of {count_to_pick}")
                if len(rand_indices_set) == 0:
                    print("done")
                    break


def write_veld_data_yaml():
    result = subprocess.run(["du", "-sh", OUT_FILE_PATH], capture_output=True, text=True)
    data_size = result.stdout.split()[0]
    result = subprocess.run(["wc", "-l", OUT_FILE_PATH], capture_output=True, text=True)
    num_lines = result.stdout.split()[0]
    veld_data_yaml = {
        "x-veld": {
            "data": {
                "description": OUT_DATA_DESCRIPTION,
                "topics": "NLP",
                "contents": [
                    "training data",
                    "raw text",
                ],
                "file_type": "txt",
                "additional": {
                    "data size": data_size,
                    "number of lines": num_lines,
                    "percentage_sample": PERCENTAGE_SAMPLE,
                    "sample_random_seed": SAMPLE_RANDOM_SEED,
                }
            }
        }
    }
    with open(OUT_VELD_DATA_YAML_PATH, "w") as f:
        yaml.dump(veld_data_yaml, f, sort_keys=False)



def main():
    try:
        os.remove(OUT_LOG_PATH)
    except:
        pass
    print(f"starting at: {datetime.now()}")
    print(f"IN_FILE_PATH: {IN_FILE_PATH}")
    print(f"OUT_FILE_PATH: {OUT_FILE_PATH}")
    print(f"SAMPLE_RANDOM_SEED: {SAMPLE_RANDOM_SEED}")
    print(f"PERCENTAGE_SAMPLE: {PERCENTAGE_SAMPLE}")
    print(f"BUFFER_SEGMENTS: {BUFFER_SEGMENTS}")
    rand_indices_set = get_line_indices()
    create_sample(rand_indices_set)
    write_veld_data_yaml()
    print(f"done at: {datetime.now()}")


if __name__ == "__main__":
    main()

