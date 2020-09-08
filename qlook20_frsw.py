#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as P
import datetime 

### ここを適宜変更 #####
DATAPATH = "/mnt/data/Tromso/obs_data/"
START_DATE = datetime.date(2019,2,7)
ave_unit = 5
#####################################

sheet_num = 0
fig_num = 20
max_ch =16384
end_file = 0

Date = START_DATE.strftime("%Y%m%d")
fig = []
ch = []
ax = []
for ii in range(max_ch):
    ch.append(int(ii))

for sheet_num in range(15):
    if (end_file == 1):
        break
    fig.append(P.figure(figsize=(10,12)))
    fig[sheet_num].subplots_adjust(hspace=0.4,wspace=0.2)
    print(sheet_num)
    for i in range(fig_num):
        ave = [0 for ii in range(max_ch)]
        flag = 0
        ave_num = ave_unit
        for n in range(0,ave_unit):
            cal = [0 for ii in range(max_ch)]
#           ch = []
            hot_a = []
            hot_s = []
            cold_a = []
            cold_s = []
            sky_a = []
            sky_s = []
            file_name = DATAPATH+"/"+Date+"/"+"EISC"+Date+"."+str(n+i*ave_unit+ave_unit*fig_num*sheet_num).zfill(5)+".txt"
            try:
                f = open(file_name)
            except IOError:
                print("file end")
                end_file = 1
                break
#           print(str(n+i*ave_unit) + " " + str(flag))
            A = f.readlines()
            for m in range(len(A)):
                if(A[m].find('Elevation Switching Method') > 0):
#                   print(str(n+i*ave_unit) + "  ELSW")
                    flag = 2
                    ave_num -= 1
                    f.close()
                    break
                if(A[m].find(';') < 0):
                    if((flag == 0) | (flag == 2)):
                        flag = 1
#                       print(str(n+i*ave_unit) + "  FRSW_data")
#                   ch.append(int(A[m].split(',')[0]))
                    hot_a.append(float(A[m].split(',')[1]))
                    hot_s.append(float(A[m].split(',')[2]))
                    cold_a.append(float(A[m].split(',')[3]))
                    cold_s.append(float(A[m].split(',')[4]))
                    sky_a.append(float(A[m].split(',')[5]))
                    sky_s.append(float(A[m].split(',')[6]))
#               if(A[m].find('Elevation Switching Method') > 0):
#                   continue
            if(flag != 2):
                for m in range(len(hot_a)):
                    cal[m] = (300-77)*(1/(hot_a[m]-cold_a[m])*(sky_a[m]-hot_a[m])-1/(hot_s[m]-cold_s[m])*(sky_s[m]-hot_s[m]))
                    ave[m] += cal[m]
            if(flag == 1):
#               print(str(n+i*ave_num) + "  FRSW_1st")
                first = str(n+i*ave_unit+ave_unit*fig_num*sheet_num).zfill(5)
                flag = 3
        last = str(n+i*ave_unit+ave_unit*fig_num*sheet_num).zfill(5)
        f.close()

#        print(ave_num)  
        if(ave_num == 0):
            f.close()
            continue        
        for m in range(len(ave)):
            ave[m] /= ave_num
                

#    fig = P.figure(figsize=(15,10))##New graph file
        print(str(sheet_num)+" "+str(i))
        ax.append(fig[sheet_num].add_subplot(5,4,i+1))
        if(i==0):
            ax[i+sheet_num*fig_num].text(0.5,0.95,Date,transform=fig[sheet_num].transFigure)
        ax[i+sheet_num*fig_num].set_title(first + " - " + last + "  " + str(ave_num) + "data")
        ax[i+sheet_num*fig_num].set_xlim(1000,16000)
        ax[i+sheet_num*fig_num].set_ylim(-5,5)
        ax[i+sheet_num*fig_num].plot(ch,ave, "-")

    P.savefig("QL_"+Date+"_"+str(sheet_num)+".png")
    P.show()

         

