# analysis.py
import numpy as np
from typing import List, Optional

def calculate_wait_times(predictions: List[int]) -> Optional[List[int]]:
    """
    Creates a list of wait times (intervals) between consecutive arrivals.

    Args:
        predictions: List of minutes until next arrivals.

    Returns:
        List of wait times (in minutes) or None if there are fewer than two predictions.
    """
    if predictions and len(predictions) > 1:
        predictions.sort() # Ensure chronological order
        # Calculate the difference between consecutive arrival times
        list_of_wait_times = [
            predictions[i+1] - predictions[i]
            for i in range(len(predictions) - 1)
        ]
        return list_of_wait_times
    else:
        list_of_wait_times = []
        list_of_wait_times.append(predictions)
        return list_of_wait_times

def find_mean_time(list_of_times: Optional[List[int]]) -> float:
    """Finds the mean of a list of times using NumPy."""
    return np.mean(list_of_times) if list_of_times else 0.0

def find_median_time(list_of_times: Optional[List[int]]) -> float:
    """Finds the median of a list of times using NumPy."""
    return np.median(list_of_times) if list_of_times else 0.0

def find_st_dev_time(list_of_times: Optional[List[int]]) -> float:
    """Finds the standard deviation of a list of times using NumPy."""
    return np.std(list_of_times) if list_of_times else 0.0