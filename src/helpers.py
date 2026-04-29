import numpy as np

def calculate_percentile(data, percentile):
    """
    Calculate a specific percentile from a list of data.
    """
    return np.percentile(data, percentile)
