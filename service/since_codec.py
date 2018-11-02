from io import StringIO


# copied from union_datasets.py
def decode_since(dataset_ids, since):
    if since in (None, "0"):
        return {}
    updated_dict = {}
    values = since.split(".")

    if len(values) != len(dataset_ids):
        raise Exception(
            ("decode_since(): The number of since-values (%d) is different from the number of dataset_ids (%d)! "
             "(This can happen if the pipe has been reconfigured with a different number of dataset_ids.)"
             "since: '%s'.  dataset_ids:'%s'"
             ) %
            (len(values), len(dataset_ids), since, dataset_ids))

    for i, dataset_id in enumerate(dataset_ids):
        value = values[i]
        if value != "":
            updated_dict[dataset_id] = int(value)
    return updated_dict


# copied from union_datasets.py
def encode_since(dataset_ids, updated_dict):
    with StringIO() as out:
        for i, dataset_id in enumerate(dataset_ids):
            if i > 0:
                out.write(".")
            if dataset_id in updated_dict:
                out.write(str(updated_dict[dataset_id]))
        out.seek(0)
        return out.read()
