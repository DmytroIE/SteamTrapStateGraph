import pandas as pd
import numpy as np


def get_file_name_from_path(path):
    return path.split("/")[-1]

def calc_integral_with_nans(pd_series):
    '''
    This function calculates the area under the curve that is described as a set of values in a pandas Series with datetime index.
    If some of these values are NA then this function doesn't "connects" the points with valid values calculating the area undr this "bridge"
    but rather excludes these "bad" parts from the sum
    '''
    index_from = 0
    index_to = 0
    integral = 0
    cumulative_time = 0
    for record in pd_series:
        if pd.isna(pd_series[index_to]) or index_to +1 == pd_series.size:
            if index_from != index_to:
                if(index_to - index_from != 1): #chunk needs at least 2 points to form the trapz which area can be calculated
                    if index_to +1 == pd_series.size and pd.notna(pd_series[index_to]):
                        index_to += 1
                    pd_chunk = pd_series.iloc[index_from:index_to]
                    np_chunk_index = pd_chunk.index.to_numpy(dtype='datetime64[s]')
                    np_chunk_data = pd_chunk.to_numpy(dtype='float64')
                    integral += np.trapz(np_chunk_data, x=np_chunk_index)
                    cumulative_time += np_chunk_index[-1]-np_chunk_index[0]
            index_to += 1
            index_from = index_to
        else:
            index_to += 1
    if cumulative_time == 0:
        return None, None
    return integral, cumulative_time





if __name__ == '__main__':

    index = pd.DatetimeIndex(['2014-07-04 12:01:33', 
                              '2014-07-04 12:31:33', 
                              '2014-07-04 13:01:33', 
                              '2014-07-04 13:31:33',
                              '2014-07-04 14:01:33',
                              '2014-07-04 14:31:33',
                              '2014-07-04 15:11:33',
                              '2014-07-04 15:31:33'])
    sr = pd.Series([20, np.nan, np.nan, 20, 20, 30, 10, np.nan], index = index)

    integ, cum_t = calc_integral_with_nans(sr)
    if integ and cum_t:
        print(f'integral = {integ}\ncumul time = {cum_t}\nmean integr = {integ/cum_t}')
    else:
        print('None')