import csv
import sys


def combine_csv_files(csv_file_path_1: str, csv_file_path_2: str, output_file_path: str):
    try:
        with open(csv_file_path_1, 'r') as f1:
            reader1 = list(csv.reader(f1))

        with open(csv_file_path_2, 'r') as f2:
            reader2 = list(csv.reader(f2))

        if reader1[0] != reader2[0]:
            print("Error: The column headers of the two files do not match.")
            return

        combined_rows = reader1 + reader2[1:]
        with open(output_file_path, 'w', newline='') as f_out:
            writer = csv.writer(f_out)
            writer.writerows(combined_rows)

        print(f"Files combined successfully into {output_file_path}")
    except FileNotFoundError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python combine_csv.py <directory_1> <directory_2>")
        exit(0)

    directory_1 = sys.argv[1].strip('/')
    directory_2 = sys.argv[2].strip('/')

    place_id = "copenhagen"
    prune_measures = ["betweenness", "closeness"]
    percentages = ["0.6_0.4", "0.85_0.15", "0.75_0.25", "0.25_0.25_0.25_0.25", "0.33_0.34_0.33"]

    for prune_measure in prune_measures:
        for percentage in percentages:
            file_name = f"{place_id}_{prune_measure}_{percentage}"
            file_path_1 = f"{directory_1}/{file_name}.csv"
            file_path_2 = f"{directory_2}/{file_name}.csv"
            combined_path = f"{file_name}.csv"

            combine_csv_files(file_path_1, file_path_2, combined_path)
