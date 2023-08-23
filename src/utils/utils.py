import pandas as pd
import numpy as np

from src.utils.settings import ResampleOperations

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

    srs_list = []

    if len(service_breaks) > 0:
        sb_prev = srs.index[0]
        #print(f'sb prev = {sb_prev}')
        for sb in service_breaks:
            #print(f'first sb = {sb}')
            if sb > sb_prev:
                chunk = srs[(srs.index>=sb_prev)&(srs.index<=sb)]
                srs_list.append(chunk)
                sb_prev = sb
            else:
                raise ValueError('Service breaks are not ordered')
        chunk = srs[(srs.index>=sb_prev)]
        srs_list.append(chunk)
    else:
        srs_list.append(srs)
    return srs_list

def resample_series(srs_list, resample_options):
    aver_method = resample_options['aver_method']
    aver_period = resample_options['aver_period']
    offset = resample_options['offset']
    resampled_srs_list = []
    match aver_method:
        case ResampleOperations.Mean:
            for srs in srs_list:
                #last_index_from_orig_srs = srs.index[-1]
                resampled_srs = srs.resample(f'{aver_period}h', origin='start', offset=f'{offset}m').mean()#.ffill(limit=1)
                #last_value_from_res_srs = resampled_srs[-1]
                #resampled_srs.loc[last_index_from_orig_srs] = last_value_from_res_srs
                resampled_srs_list.append(resampled_srs)
        case ResampleOperations.NoResample:
            resampled_srs_list = srs_list
        case _:
            resampled_srs_list = srs_list
    return resampled_srs_list

def convert_sbs_to_pd_format(service_breaks):
    pd_format_sbs = []
    for sb in service_breaks:
        pd_format_sbs.append(pd.to_datetime(sb))
    return pd_format_sbs

def steam_Iq_make_cold_state_interval_list_for_series(cycle_srs, srs, num_of_points = 2):
    if num_of_points < 2:
        raise ValueError('To create interval at least 2 spoints are needed')
    
    srs_interv_list = []
    int_idx = 0

    while int_idx < cycle_srs.size:
        if abs(cycle_srs[int_idx]) < 1e-9 and abs(srs[int_idx]) < 1e-9:
            #start = cycle_srs.index[int_idx]
            # end_int_idx = int_idx + point_number
            # if end_int_idx > cycle_srs.size:
            #     end_int_idx = cycle_srs.size
            chunk_cs = cycle_srs.iloc[int_idx:]
            chunk_s = srs.iloc[int_idx:]
            i = 0
            for a, b in zip(chunk_cs, chunk_s):
                if abs(a) < 1e-9 and abs(b) < 1e-9:
                    if i == chunk_cs.size-1:
                        if i<num_of_points-1:
                            int_idx += i + 1
                            break
                        else:
                            srs_interv_list.append((chunk_cs.index[0], chunk_cs.index[i]))
                            int_idx += i + 1
                            break
                    i += 1
                    continue

                else:
                    if i<num_of_points:
                        int_idx += i + 1
                        break
                    else:
                        srs_interv_list.append((chunk_cs.index[0], chunk_cs.index[i-1]))
                        int_idx += i + 1
                        break
        else:
            int_idx += 1

    return srs_interv_list

def extract_series_from_df(df, from_, to, col_name):
    if from_ < to:
            srs = df[col_name]
            return srs[(srs.index>=from_)&(srs.index<=to)]
    else:
        raise ValueError('Mismatch in the plot dates')


 # add to plot function to create a stem diagram

                # srs = extract_series_from_df(self._data, plot_from, plot_to, 'Aver leak')
                # markerline, stemlines, baseline = self._plt.stem(
                #     srs.index, srs, linefmt='white', markerfmt='None', bottom=-5.0)
                # final_status_srs = extract_series_from_df(self._data, plot_from, plot_to, 'Final status')
                # color_map = []
                # for r in final_status_srs.values:
                #     match r:
                #         case 1:
                #             color_map.append('cyan')
                #         case 2:
                #             color_map.append('green')
                #         case 3:
                #             color_map.append('orange')
                #         case 4:
                #             color_map.append('red')
                #         case _:
                #             color_map.append('white')
                # stemlines.set(linewidth=0.5, color=color_map)
                # # markerline.set_markerfacecolor('none')
                # # print(f'{stemlines=}')
                # # for line in stemlines:
                #     #line.set(linewidth=10.0)
                #     # print(f'{line=}')
                #     # line.set_color('red')
                #     # line.set_linewidth(10.0)
                # return

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

    # for sr in test_list:
    #     result = calc_integral_numpy_types(sr)
    #     print('---------results Numpy datatype-------------')
    #     if result:
    #         print(f'integral_np = {result[0]}\ncumul time_np = {result[1]}')
    #         print(f'mean_integr_np = {result[0]/result[1]}')
    #         print(f'loss_np = {result[0]* 15}')
    #     else:
    #         print('None_np')
            
    #     print('\n')
            
    #     result = calc_integral(sr)
    #     print('---------results Pandas datatype-------------')
    #     if result:
    #         print(f'integral = {result[0]}\ncumul time = {result[1]}')
    #         print(f'mean integr = {result[0]/result[1]}')
    #         print(f'loss = {result[0].total_seconds()* 15}')
    #     else:
    #         print('None_pd')
    #     print('-----------------------------------------\n')
    index2 = pd.DatetimeIndex(['2014-07-04 12:01:33', 
                          '2014-07-04 12:31:33', 
                          '2014-07-04 13:01:33', 
                          '2014-07-04 13:31:33',
                          '2014-07-04 14:01:33',
                          '2014-07-04 14:31:33',
                          '2014-07-04 15:01:33',
                          '2014-07-04 15:31:33',
                          '2014-07-04 16:01:33',
                          '2014-07-04 16:31:33',
                          '2014-07-04 17:01:33'])
    test_cs = pd.Series([2,0,0,1,2,0,1,2,0,0,0], index = index2)
    test_s = pd.Series([6,0,0,7,8,0,5,3,0,0,0], index = index2)
    print(steam_Iq_make_cold_state_interval_list_for_series(test_cs, test_s, 3))
