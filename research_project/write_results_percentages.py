
def write_result_with_percentages(res:dict, mode:str, placeid:str, iteration:str, poi_source, prune_measure:str, suffix:str, dictnested = {}):

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

    with open(PATH["results"] + placeid + "/" + "iteration/" + iteration + "/" + filename, openmode) as f:
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
