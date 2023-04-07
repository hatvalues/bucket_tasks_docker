import csv

def preproc_csv(file_name : str, header_row=0):
    """Convenience function for csv file.
    
    Parameters
    ----------
    file_name : str
        Path to file
    header_row : int
        Where to find the headers (zero if none). Will skip prior rows.

    Returns
    -------
    List of dict (headers) or list of list (no headers)
    
    """
    if header_row:
        with open(file_name, "r") as f:
            for _ in range(header_row):
                headers = next(f).strip().split(",")
            data = []
            for row in csv.DictReader(f, fieldnames=headers):
                data.append(row)
        return data
    else: # no headers
        pass