import pandas as pd
import numpy as np


def get_file_name_from_path(path):
    return path.split("/")[-1]


def calc_integral_numpy_types(pd_series):
    '''
    This function calculates the area under the curve that is described as a set of values in a pandas Series with datetime index.
    If some of these values are NA then this function doesn't "connects" the points with valid values calculating the area undr this "bridge"
    but rather excludes these "bad" parts from the sum. It uses operations with numpy datatypes and returns the results as numpy
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
                    #print(f'integral={integral}')
                    cumulative_time += np_chunk_index[-1]-np_chunk_index[0]
            index_to += 1
            index_from = index_to
        else:
            index_to += 1
    if cumulative_time == 0:
        return None
    return (integral, cumulative_time)

def calc_integral(pd_series):
    '''
    This function calculates the area under the curve that is described as a set of values in a pandas Series with datetime index.
    If some of these values are NA then this function doesn't "connects" the points with valid values calculating the area undr this "bridge"
    but rather excludes these "bad" parts from the sum. It uses operations with pandas datatypes and returns the results as pd Timedelta
    '''
    index_from = 0
    index_to = 0
    integral = pd.Timedelta(0)
    cumulative_time = pd.Timedelta(0)
    for record in pd_series:
        if pd.isna(pd_series[index_to]) or index_to +1 == pd_series.size:
            if index_from != index_to:
                if(index_to - index_from != 1): #chunk needs at least 2 points to form the trapz which area can be calculated
                    if index_to +1 == pd_series.size and pd.notna(pd_series[index_to]):
                        index_to += 1
                    chunk = pd_series.iloc[index_from:index_to]
                    integral += np.trapz(chunk, x=chunk.index.astype('datetime64[s]'))
                    #print(f'integral2={integral}')
                    timedelta = chunk.index[-1]-chunk.index[0]
                    cumulative_time += timedelta
            index_to += 1
            index_from = index_to
        else:
            index_to += 1
    if cumulative_time.total_seconds() == 0:
        return None
    return (integral, cumulative_time)

def split_one_series_by_sb(srs, service_breaks):
    return [srs]

def resample_series(srs_list, resample_options):
    return srs_list





if __name__ == '__main__':

    index = pd.DatetimeIndex(['2014-07-04 12:01:33', 
                              '2014-07-04 12:31:33', 
                              '2014-07-04 13:01:33', 
                              '2014-07-04 13:31:33',
                              '2014-07-04 14:01:33',
                              '2014-07-04 14:31:33',
                              '2014-07-04 15:01:33',
                              '2014-07-04 15:31:33'])
                              
    sr_err = pd. Series([20], index = pd.DatetimeIndex(['2014-07-04 12:01:33']))
    sr_1 = pd.Series([20, 50, np.nan, 20, 20, 30, 10, np.nan], index = index)
    sr_2 = pd.Series([20, np.nan, np.nan, 20, 20, 30, 10, np.nan], index = index)

    test_list = [sr_err, sr_1, sr_2]

    for sr in test_list:
        result = calc_integral_numpy_types(sr)
        print('---------results Numpy datatype-------------')
        if result:
            print(f'integral_np = {result[0]}\ncumul time_np = {result[1]}')
            print(f'mean_integr_np = {result[0]/result[1]}')
            print(f'loss_np = {result[0]* 15}')
        else:
            print('None_np')
            
        print('\n')
            
        result = calc_integral(sr)
        print('---------results Pandas datatype-------------')
        if result:
            print(f'integral = {result[0]}\ncumul time = {result[1]}')
            print(f'mean integr = {result[0]/result[1]}')
            print(f'loss = {result[0].total_seconds()* 15}')
        else:
            print('None_pd')
        print('-----------------------------------------\n')