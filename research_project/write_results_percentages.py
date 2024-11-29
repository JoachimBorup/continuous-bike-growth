import os
def write_result_with_percentages(
        res:dict,
        mode:str, 
        placeid:str,
        subgraph_percentage:str, 
        iteration:str, 
        poi_source, 
        prune_measure:str, 
        suffix:str, 
        dictnested = {}):

    """Write results (pickle or dict to csv)
    """
    if mode == "pickle":
        openmode = "wb"
    else:
        openmode = "w"

    if poi_source:
        filename = placeid + '_poi_' + poi_source + "_" + prune_measure + suffix
    else:
        filename = placeid + "_" + prune_measure + suffix

    file_path = f'{PATH["results"]}{placeid}/{subgraph_percentage}/{iteration}/{filename}'
    dir_path = os.path.dirname(file_path)  # Extract directory path

    # Ensure the directory exists before opening the file
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)

    # Open the file safely
    with open(file_path, openmode) as f:
        if mode == "pickle":
            pickle.dump(res, f)
        elif mode == "dict":
            w = csv.writer(f)
            w.writerow(res.keys())
            try: # dict with list values
                w.writerows(zip(*res.values()))
            except: # dict with single values
                w.writerow(res.values())
        elif mode == "dictnested":
            # https://stackoverflow.com/questions/29400631/python-writing-nested-dictionary-to-csv
            fields = ['network'] + list(dictnested.keys())
            w = csv.DictWriter(f, fields)
            w.writeheader()
            for key, val in sorted(res.items()):
                row = {'network': key}
                row.update(val)
                w.writerow(row)