#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as P
import math as M
#import reform_lib as L
#import reform_cfg as C

T_HOT = 300
T_COLD = 77
DATAPATH = "/Volumes/Yuta_Bak5/obs_data/20190108/EISC20190108."
start_num = 50
end_num = 150

def Read_header(A):
    global center_freq, center_ch, ch_width, sb1, sb2, sb3, lo1_a, lo1_s
    global lo2_a, lo2_s, d_type, tau
    
    if(A.find('Rest')>=0):
        center_freq = float((A.split(',')[1]).split(' ')[0])
    if(A.find('Center Ch')>=0):
        center_ch = float((A.split(',')[1]).split(' ')[0])
    if(A.find('Channel Width')>=0):
        ch_width = float((A.split(',')[1]).split(' ')[0])
    if(A.find('1st Mixer')>=0):
        hoge = (A.split(',')[1]).split(' ')[0]
        if(hoge == 'upper'):
            sb1 = 1
        if(hoge == 'lower'):
            sb1 = -1        
    if(A.find('2nd Mixer')>=0):
        hoge = (A.split(',')[1]).split(' ')[0]
        if(hoge == 'upper'):
            sb2 = 1
        if(hoge == 'lower'):
            sb2 = -1        
    if(A.find('3rd Mixer')>=0):
        hoge = (A.split(',')[1]).split(' ')[0]
        if(hoge == 'upper'):
            sb3 = 1
        if(hoge == 'lower'):
            sb3 = -1
    if(A.find('(1st Local Frequency')>=0):
        lo1_a = float((A.split(',')[1]).split(' ')[0])
    if(A.find('Altanative 1st Local')>=0):
        lo1_s = float((A.split(',')[1]).split(' ')[0])
    if(A.find('(2nd Local Frequency)')>=0):
        lo2_a = float((A.split(',')[1]).split(' ')[0])
    if(A.find('Altanative 2nd Local')>=0):
        lo2_s = float((A.split(',')[1]).split(' ')[0])
    if(A.find('Data Type')>=0):
        if(A.find('EL')>=0):
            d_type = 'ELSW'
        if(A.find('F')>=0):
            d_type = 'FRSW'
    if(A.find('tau')>=0):
        tau = float((A.split(',')[1]).split(' ')[0])

### Reform program ###
def Reform(file_name):
    global center_freq, center_ch, ch_width, sb1, sb2, sb3, lo1_a, lo1_s
    global lo2_a, lo2_s, d_type, tau, rfm, freq

    ch = []
    hot_a = []
    hot_s = []
    cold_a = []
    cold_s = []
    sky_a = []
    sky_s = []
    cal = []
    freq = []
    add = []
    sub = []
    add_sub = []
    rfm = []

    try:
        f = open(file_name)
    except IOError:
        print("No file")
        return(-1)
    f_out = open(file_name+".rfm", mode='w')
    A = f.readlines()
    for m in range(len(A)):
        Read_header(A[m])
        if(A[m].find(';')<0 and d_type == 'ELSW'):
            ch.append(float(A[m].split(',')[0]))
            hot_a.append(float(A[m].split(',')[1]))
            cold_a.append(float(A[m].split(',')[2]))
            sky_a.append(float(A[m].split(',')[3]))
            sky_s.append(float(A[m].split(',')[4]))
        if(A[m].find(';')<0 and d_type == 'FRSW'):
            ch.append(float(A[m].split(',')[0]))
            hot_a.append(float(A[m].split(',')[1]))
            hot_s.append(float(A[m].split(',')[2]))
            cold_a.append(float(A[m].split(',')[3]))
            cold_s.append(float(A[m].split(',')[4]))        
            sky_a.append(float(A[m].split(',')[5]))
            sky_s.append(float(A[m].split(',')[6]))
    f.close()

    if(d_type == 'ELSW'):
        return(0)
        for m in range(len(hot_a)):
            freq.append(center_freq + sb1 * sb2 * sb3 * (ch[m]-center_ch) * ch_width)
            cal.append((300-77)*(sky_a[m]-sky_s[m])/(hot_a[m]-cold_a[m]))   #ELSW
    if(d_type == 'FRSW'):
        for m in range(len(hot_a)):
            freq.append(center_freq + sb1 * sb2 * sb3 * (ch[m]-center_ch) * ch_width)
            add.append(float((T_HOT - T_COLD)/(hot_a[m] - cold_a[m])*(sky_a[m] - cold_a[m])))
            sub.append(float((T_HOT - T_COLD)/(hot_s[m] - cold_s[m])*(sky_s[m] - cold_s[m])))
            add_sub.append(float(add[m]-sub[m]))
            rfm.append(float(m))

    #reform
    delta_1st = lo1_a - lo1_s
    delta_2nd = lo2_a - lo2_s
    sb = sb1 * sb2 * sb3
    delta_f = sb * delta_1st + sb2 * sb3 * delta_2nd
    delta_ch = delta_f / ch_width
    i_delta_ch = M.floor(delta_ch)
    f_delta_ch = delta_ch - i_delta_ch

    #print(delta_ch, i_delta_ch, f_delta_ch, len(hot_a))
    if(i_delta_ch > 0):
        for m in range(0,len(hot_a)-i_delta_ch-1):
            rfm[m] = (add_sub[m]-(add_sub[m+i_delta_ch]*(1.0-f_delta_ch)+add_sub[m+i_delta_ch+1])*(f_delta_ch))/2
    if(i_delta_ch < 0):
        i_delta_ch *= -1
        for m in range(i_delta_ch, len(hot_a)):
            rfm[m] = (add_sub[m]-(add_sub[m-i_delta_ch]*f_delta_ch+add_sub[m-i_delta_ch+1])*(1 - f_delta_ch))/2

    # atmospheric correction
    for m in range(len(hot_a)):
        rfm[m] = M.exp(tau) * rfm[m]
    # Plot
#    P.xlim(100,16000)
#    P.ylim(-5,5)
#    P.plot(freq,rfm,'-')
#    P.show()
    return(len(hot_a))
    
'''    ## file out
    f_out = open(file_name+".rfm", mode='w')
    for m in range(len(A)):
        if(A[m].find(';')>=0):
            f_out.write(A[m])
    for m in range(len(hot_a)):
        f_out.write('{:05.0f},{:24.16e},{:24.16e},{:24.16e}\n'.format(m,add[m], sub[m],rfm[m]))
    f_out.close()
'''


### Main program ###
avg = []
ch = []
n_ave = 0
for num in range(start_num, end_num):
    file_name = DATAPATH+str(num).zfill(5)+".txt"
    ch_max = Reform(file_name)
    if(ch_max < 0):
        continue
    print(file_name+":"+d_type)
    if(d_type == "FRSW"):
        if(n_ave == 0):
            for m in range(ch_max):
                avg.append(float(rfm[m]))
                ch.append(float(m))
        else:
            for m in range(ch_max):
                avg[m] = n_ave * avg[m] + rfm[m]
                avg[m] /= n_ave+1
        n_ave += 1
        
P.xlim(250300,251300)
P.ylim(-1,1)
P.plot(freq,avg,'-')
P.show()

