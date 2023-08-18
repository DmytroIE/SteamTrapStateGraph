import pandas as pd
import numpy as np
import math

MARGIN_FOR_INTERVAL_FLOOR = 0.05
DEF_THRESHOLD_FOR_GOOD = 10.0
DEF_THRESHOLD_FOR_AVERAGE = 25.0


def set_sample_status(row):
    #print(f'row={row}')
    #print(f'row type={type(row)}')
    status = 1 #Hot
    if abs(row['Leak'])<0.00001 and abs(row['Cycle Counts'])<0.00001:
        status = 0
    elif pd.isna(row['Leak']) or pd.isna(row['Cycle Counts']):
        status = -1
    return status

def apply_mode(srs):
    s = srs.astype('int64')
    mode_srs = s.mode()
    if mode_srs.size>1: #means that we have the situation when all 3 samples have diff value, then just choose the last one
        return s[-1]
    else:
        return mode_srs[0]



class SteamIqToolSet():
    @staticmethod
    def fill_data_gaps_with_nans(df, interval='1H'):
        '''Fills the gaps that are bigger than "interval" with np.NaN'''

        if len(df.index) < 2:
            raise ValueError('At least 2 spoints in dataframe are needed')
        
        idx = 0
        nan_chunks = []
        length = len(df.index)
        timedelta = pd.Timedelta(interval)
        while idx<length-1:
            if df.index[idx+1]-df.index[idx]>timedelta:
                num_of_intervals = int((df.index[idx+1] - df.index[idx]) / timedelta - MARGIN_FOR_INTERVAL_FLOOR)
                #print(num_of_intervals)
                if(num_of_intervals>0):
                    new_interval = ((df.index[idx+1] - df.index[idx]) / (num_of_intervals + 1))
                    #print(new_interval)
                    #print(df.index[idx])
                    index = [(df.index[idx]+new_interval*(i+1)).floor('1s') for i in range(num_of_intervals)]
                    nans = [np.NaN for i in range(num_of_intervals)]
                    t = pd.DataFrame({'Leak': nans, 'Cycle Counts': nans}, index=index)
                    # print(t)
                    # nan_chunk = df.iloc[idx:idx+1+1]
                    # print(nan_chunk)
                    # nan_chunk = pd.concat([nan_chunk, t]).sort_index()
                    # print(nan_chunk)
                    nan_chunks.append(t)
            idx += 1
        nan_chunks.append(df)
        resampled = pd.concat(nan_chunks).sort_index()
        return resampled

    @staticmethod
    def set_sample_statuses(df):
        df['Sample status'] = df.apply(set_sample_status, axis=1)

    @staticmethod
    def set_averaged_sample_statuses(df):
        # calculate mode
        df['Mode'] = (df['Sample status'].rolling(window=3, min_periods=1).apply(apply_mode)).astype('int64')
        #df['Mode'] = df['Mode'].astype('int64')
        df['Aver status'] = [0 for x in range(len(df.index))]
        
        # apply averaged statuses
        i = 0
        while i<len(df.index):
            if df.iloc[i, 2]==-1:
                df.iloc[i, 4]=-1
            elif df.iloc[i, 3]==-1:
                df.iloc[i, 4]=df.iloc[i, 2]
            else:
                df.iloc[i, 4]=df.iloc[i, 3]
            i += 1

        
        #pull up some values
        df['Pulled aver status'] = [0 for x in range(len(df.index))]
        i = 0
        while i<len(df.index)-1:
            if df.iloc[i, 2] != df.iloc[i, 4]:
                if df.iloc[i, 2] == df.iloc[i+1, 4]:
                    df.iloc[i, 5] = df.iloc[i, 2]
                else:
                    df.iloc[i, 5] = df.iloc[i, 4]
            else:
                if df.iloc[i, 2]==-1 and df.iloc[i+1, 4]==-1:
                    df.iloc[i, 5] = df.iloc[i, 2]
                else:
                    df.iloc[i, 5] = df.iloc[i, 4]
            i += 1
        df.iloc[-1, 5] = df.iloc[-1, 2] #the last sample takes the current status untill a new sample is delivered

    @staticmethod
    def set_final_statuses(df):
        df['Aver leak'] = [np.NaN for x in range(len(df.index))]
        df['Final status'] = [0 for x in range(len(df.index))]
        
        def set_status(df, idx):
            if df.iloc[idx, 5]==1:
                if df.iloc[idx, 6]<=DEF_THRESHOLD_FOR_GOOD:
                    df.iloc[idx, 7] = 2 #low intensive
                elif df.iloc[idx, 6]<=DEF_THRESHOLD_FOR_AVERAGE:
                    df.iloc[idx, 7] = 3 #mid intensive
                else:
                    df.iloc[idx, 7] = 4 #high intensive
            elif df.iloc[idx, 5]==0:
                df.iloc[idx, 6] = 0.0
                df.iloc[idx, 7] = 1 #cold
            else:
                df.iloc[idx, 7] = 0 #offline
 
        # cycle_col_idx = df.columns.get_loc('Cycle Counts')
        leak_col_idx = df.columns.get_loc('Leak')

        #first point
        if df.iloc[0, 5]==1:
            df.iloc[0, 6] = df.iloc[0, leak_col_idx]
            if df.iloc[1, 5]==1:
                df.iloc[0, 6] = (df.iloc[0, 6] + df.iloc[1, leak_col_idx]) / 2
        set_status(df, 0)
        #last point
        idx_of_last_point = len(df.index) - 1
        if df.iloc[idx_of_last_point, 5]==1:
            df.iloc[idx_of_last_point, 6] = df.iloc[idx_of_last_point, leak_col_idx]
            if df.iloc[idx_of_last_point-1, 5]==1:
                df.iloc[idx_of_last_point, 6] = (df.iloc[idx_of_last_point-1, leak_col_idx] + df.iloc[idx_of_last_point, 6]) / 2
        set_status(df, idx_of_last_point)
 
        i = 1
        divider = 1
        while i < idx_of_last_point:
            #calculate mean leak for max 3 adjacent "Hot" samples - centered around the point
            if df.iloc[i, 5]==1:
                divider = 1
                df.iloc[i, 6] = df.iloc[i, leak_col_idx]
                if df.iloc[i+1, 5]==1:
                    df.iloc[i, 6] = df.iloc[i, 6] + df.iloc[i+1, leak_col_idx]
                    divider += 1
                if df.iloc[i-1, 5]==1:
                    df.iloc[i, 6] = df.iloc[i, 6] + df.iloc[i-1, leak_col_idx]
                    divider += 1
                df.iloc[i, 6] = df.iloc[i, 6] / divider    
            set_status(df, i)

            i += 1
            
    @staticmethod
    def prepare_status_map(srs, filter=4):
        if srs.size < 2:
            raise ValueError('At least 2 spoints in dataframe are needed')
        
        ind_from = 0
        ind_to = 0
        status_map = {'0': [], '1': [], '2': [], '3': [], '4': []}
        non_zero_chunks = []
        opening_of_curr_zero_interval = None

        while ind_to<srs.size:
            if srs[ind_to]==0: #or ind_to+1==srs.size:
                if ind_from!=ind_to:
                    if(ind_to-ind_from!=1): #non-zero-chunk needs at least 2 points
                        #if ind_to+1==srs.size and srs[ind_to]>0:
                        #    ind_to += 1
                        non_zero_chunk = srs.iloc[ind_from:ind_to]
                        non_zero_chunks.append(non_zero_chunk)
                        if not opening_of_curr_zero_interval:
                            opening_of_curr_zero_interval = non_zero_chunk.index[-1]
                    else: #it means ind_to-ind_from=1, so neglect this one non-zero point and include it into the nearest from the left zero interval
                        if len(status_map['0']):
                            opening_of_curr_zero_interval = status_map['0'][-1][0]
                            status_map['0'].pop()
                        else: #maybe this is the situation like not0, 0 from the very beginning
                            opening_of_curr_zero_interval = srs.index[ind_from]
                        if ind_to==srs.size-1:
                            status_map['0'].append([opening_of_curr_zero_interval, srs.index[ind_to]])
                            opening_of_curr_zero_interval = None
                elif ind_to==0: #the first sample is zero
                    opening_of_curr_zero_interval = srs.index[ind_to]
                elif ind_to==srs.size-1:
                    status_map['0'].append([opening_of_curr_zero_interval, srs.index[ind_to]])
                    opening_of_curr_zero_interval = None
                ind_to += 1
                ind_from = ind_to
            else:
                if opening_of_curr_zero_interval:
                    #if ind_to+1==srs.size: #if there is one non-zero point at the end
                    #    status_map['0'].append([opening_of_curr_zero_interval, srs.index[ind_to]])
                    status_map['0'].append([opening_of_curr_zero_interval, srs.index[ind_to]])
                    opening_of_curr_zero_interval = None
                elif ind_to==srs.size-1 and ind_to-ind_from>0:
                    non_zero_chunk = srs.iloc[ind_from:ind_to+1]
                    non_zero_chunks.append(non_zero_chunk)

                ind_to += 1

        # extracting different non-zero states
        #print('\nStatus map begins\n')
        for aver_ch in non_zero_chunks:
            #print('Chunk')
            curr_stat = aver_ch[0]
            opening_of_curr_stat_interval = aver_ch.index[0]
            idx_to = 1
            while idx_to<aver_ch.size-1:
                if aver_ch[idx_to]!=curr_stat:
                    status_map[str(curr_stat)].append([opening_of_curr_stat_interval, aver_ch.index[idx_to]])
                    curr_stat = aver_ch[idx_to]
                    opening_of_curr_stat_interval = aver_ch.index[idx_to]
                    idx_to += 1
                else:
                    idx_to += 1
            status_map[str(curr_stat)].append([opening_of_curr_stat_interval, aver_ch.index[idx_to]])
            
        #print('\nStatus map\n\n')
        #print(f'{status_map}')
        return status_map

    @staticmethod
    def calculate_integral_values_using_sm(srs, status_map, use_green=False):
        statuses_to_use=['3', '4']
        if use_green:
            statuses_to_use=['2', '3', '4']
        integral = pd.Timedelta(0)
        cumulative_time = pd.Timedelta(0)
        for st in statuses_to_use:
            for interval in status_map[st]:
                    chunk = srs.loc[interval[0]:interval[1]]
                    integral += np.trapz(chunk, x=chunk.index.astype('datetime64[s]'))
        for st in statuses_to_use:
            for interval in status_map[st]:
                    chunk = srs.loc[interval[0]:interval[1]]
                    timedelta = chunk.index[-1]-chunk.index[0]
                    cumulative_time += timedelta
        if cumulative_time.total_seconds() == 0:
            return None
        return (integral, cumulative_time)

    @staticmethod
    def transf_percent_leak_srs_to_kgh(perc_srs, pres, orif_d):
        def leakage(perc):
            '''Returns kg/h of leakage taking % of leak rate from SteamIQ'''
            return perc*47.12*(orif_d/25.4)*(orif_d/25.4)*math.pow(pres*14.50377+14.7, 0.97)*0.7*0.36*0.45359/100.0
            # 0.45359 is a conversion coefficient from lb to kg
        
        transf_srs = perc_srs.apply(leakage)
        return transf_srs
    
    @staticmethod
    def transf_percent_leak_srs_to_kW(perc_srs, pres, orif_d, eff, entalpy):
        def leakage(perc):
            '''Returns kW of leakage based on hfg taking % of leak rate from SteamIQ
            If it is necessary to express it in kW of fuel, then it is necessary to divide this value to efficiency (usually ~0.8)
            '''
            return perc*47.12*(orif_d/25.4)*(orif_d/25.4)*math.pow(pres*14.50377+14.7, 0.97)*0.7*0.36*0.45359/100.0 * entalpy/3600.0 / (eff/100.0)
            #!!!!!!!!!add more precise formula instead of 2100.0/3600.0 
        
        transf_srs = perc_srs.apply(leakage)
        return transf_srs


if __name__ == '__main__':

    index = pd.DatetimeIndex(['2014-07-04 10:01:34', 
                              '2014-07-04 12:31:33', 
                              '2014-07-04 15:01:33', 
                              '2014-07-04 16:31:31',
                              '2014-07-04 17:01:29',
                              '2014-07-04 23:01:26',
                              '2014-07-05 00:01:25',
                              '2014-07-05 01:01:33',
                              '2014-07-05 04:01:31'])
                              

    sr_1 = pd.DataFrame({'Leak':[20, 50, 45, 20, 20, 30, 0, 61, 6], 'Cycle Counts':[5, 7, 2, 4, 6, 11, 0, 11, 2]}, index = index)

    new_df = SteamIqToolSet.fill_data_gaps_with_nans(sr_1)
    # print('After adding nans')
    # print(new_df)
    SteamIqToolSet.set_sample_statuses(new_df)
    # print('After adding statuses')
    # print(new_df)
    SteamIqToolSet.set_averaged_sample_statuses(new_df)
    # print('After adding averaged statuses')
    # print(new_df)
    # print(new_df.dtypes)
    SteamIqToolSet.set_final_statuses(new_df)
    print('After adding final statuses')
    #print(new_df)
    #print(new_df.dtypes)
    sm = SteamIqToolSet.prepare_status_map(new_df['Final status'])
    #print(sm)
    print('\n---------------------------------------------------------------\n')
    index_2 = pd.DatetimeIndex(['2014-07-04 11:01:34', 
                          '2014-07-04 12:01:34', 
                          '2014-07-04 13:01:34', 
                          '2014-07-04 14:01:34',
                          '2014-07-04 15:01:34',
                          '2014-07-04 16:01:34',
                          '2014-07-04 17:01:34',
                          '2014-07-04 18:01:34',
                          '2014-07-04 19:01:34',
                          '2014-07-04 20:01:34',
                          '2014-07-04 21:01:34',
                          ])
    sr_2 = pd.Series([0, 0, 2, 3, 4, 0, 3, 4, 0, 3, 3], index=index_2)

    sm_2 = SteamIqToolSet.prepare_status_map(sr_2)
    print(sm_2)

