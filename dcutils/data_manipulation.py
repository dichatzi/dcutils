import pandas as pd

"""
FIND INDEX
"""
def idx(inp_array, value):

    # Check if input array is a pandas series and transform it to list if this is the case
    if isinstance(inp_array, pd.Series):
        array = inp_array.to_list()
    else:
        array = inp_array
        
    # Check if the value exists in the array
    if value in array:
        return array.index(value)
    else:
        return -1

"""
FIND MATCHING INDICES
"""
def matching_idx(array1, value1, array2, value2):

    # Check if lists are pandas series and transform to lists
    if isinstance(array1, pd.Series):
        list1 = array1.to_list()
    else:
        list1 = array1
        
    if isinstance(array2, pd.Series):
        list2 = array2.to_list()
    else:
        list2 = array2
    
    try:
        return [index for index, (val1, val2) in enumerate(zip(list1, list2)) if val1 == value1 and val2 == value2]
    except:
        return -1


def dataframe_index(df:pd.DataFrame, conditions:dict):
    """
    Find rows in a DataFrame where specific columns have specific values.

    :param df: Pandas DataFrame to search in.
    :param conditions: Dictionary where keys are column names and values are the values to search for in those columns.
    :return: Indices of rows that match all the specified conditions.
    """
    # Start with a mask that marks all rows as True
    mask = pd.Series([True] * len(df))

    # Update the mask for each condition
    for column, value in conditions.items():
        mask = mask & (df[column] == value)

    # Find row indices where all conditions are met
    return df.index[mask].tolist()