import os, re, arcpy
from tabula import read_pdf
import pandas as pd
from datetime import datetime
start_time = time.time()

arcpy.env.OverwriteOutput = True

#Variables
traffic_count_folder = 'C:/GIS_Processing/TrafficCounts/FullTrafficSignalCopy/ATD Peak Hour Final'
intersection_count_excel = 'C:/GIS_Processing/TrafficCounts/IntersectionCount.csv'
aurora_address_composite = "N:/PWD/Sidewalk Ice and Drainage Complaints/GIS/AuroraAddressComposite"
folder = 'C:/GIS_Processing/TrafficCounts'
temp_GDB = 'C:/GIS_Processing/TrafficCounts/temp_GDB.gdb'
turning_movement_count = 'C:/GIS_Processing/TrafficCounts/temp_GDB.gdb/traffic_count_turning_movement'

#List all docs in folder
traf_count_folder_list = os.listdir(traffic_count_folder)

#Dataframe setup
pd.set_option("display.max_columns", None)
df_fin = pd.DataFrame()

#Lists and text to drop and populate
filter_list = [' SAT',' RAMPS', 'NB', 'SB', 'WB', 'RAMP', '(1)', '(2)', '(3)', '-PM']
filter_pdf = ['.pdf']
drop_after = '_'

#
for i in traf_count_folder_list:
    df = read_pdf(traffic_count_folder+'/'+i, pages=1)
    for f in filter_pdf:
        i = i.replace(f, '')
        name = i
    if i.endswith('-AM'):
        i = i[:-3]
    elif i.endswith('-AM (2)'):
        i = i[:-7]
    elif i.endswith('-AM (3)'):
        i = i[:-7]
    elif i.endswith('-Noon'):
        i = i[:-5]
    elif i.endswith('-Noon (2)'):
        i = i[:-9]
    for l in filter_list:
        if l in i:
            i = i.replace(l, '')
    i = i.replace('-', ' & ')
    i = i.replace('I & 70EB', 'I-70 HWY')
    i = i.replace('I & 70', 'I-70 HWY')
    i = i.replace('E & 470', 'E-470 HWY')
    i = i.replace('I & 225', 'I-225 HWY')
    i = i.split(drop_after, 1)[0]
    print(name)
    df = (df[0])
    if df.isin(['#####']).any(axis=None):
        try:
            df['Start Time'] = df['Start Time'].replace(['Count Total'], i)
            df = df.loc[df['Start Time'] == i]
            df.set_index('Start Time', inplace=True)
            print('Peak Hour has #### and changed to Count Total')
        except:
            print('##### FOUND AND ISSUES CHANGING TO COUNT TOTAL')
    else:
        if 'Start Time' in df.columns:
            try:
                df['Start Time'] = df['Start Time'].replace(['Peak Hour'], i)
                df = df.loc[df['Start Time']== i]
                df.set_index('Start Time', inplace=True)
                print('This one is normal')
            except:
                print(i+ ' FAILED EPICALLY')
        else:
            df['Unnamed: 0'] = df['Unnamed: 0'].replace(['Peak Hour'], i)
            df = df.rename(columns={'Unnamed: 0':'Start Time'}, inplace=True)
            df = df.loc[df['Start Time']== i]
            df.set_index('Start Time', inplace=True)
            print('This one has issues with column headers')
    df['Address'] = i
    df['PDF Name'] = name
    df_fin = pd.concat([df, df_fin], ignore_index=False)
df_fin = df_fin.rename(columns={'Start Time':'Peak Hour or Total', 'U-Turn':'EB_UTurn', 'Left':'EB_Left', 'Thru':'EB_Thru', 'Right':'EB_Right', 'U-Turn.1':'WB_UTurn', 'Left.1':'WB_Left', 'Thru.1':'WB_Thru', 'Right.1':'WB_Right', 'U-Turn.2':'NB_UTurn', 'Left.2':'NB_Left', 'Thru.2':'NB_Thru', 'Right.2':'NB_Right', 'U-Turn.3':'SB_UTurn', 'Left.3':'SB_Left', 'Thru.3':'SB_Thru', 'Right.3':'SB_Right', 'West':'Ped_West', 'East':'Ped_East', 'South':'Ped_South', 'North':'Ped_North'})
df_fin = df_fin.replace(',', '', regex=True)

df_fin.to_csv(intersection_count_excel, index = False)

#Check to see if FC exists - won't overwrite for some reason
if arcpy.Exists(turning_movement_count):
    arcpy.Delete_management(turning_movement_count)

#Geocode 'address' column (built from pdf name)
arcpy.GeocodeAddresses_geocoding(intersection_count_excel, aurora_address_composite, "'Single Line Input' Address VISIBLE NONE", turning_movement_count, "STATIC")

#Field cleanup work
keep_list=['USER_Address', 'USER_EB_UTurn', 'USER_EB_Left', 'USER_EB_Thru', 'USER_EB_Right', 'USER_WB_UTurn', 'USER_WB_Left', 'USER_WB_Thru', 'USER_WB_Right', 'USER_NB_UTurn', 'USER_NB_Left', 'USER_NB_Thru', 'USER_NB_Right', 'USER_SB_UTurn', 'USER_SB_Left', 'USER_SB_Thru', 'USER_SB_Right', 'USER_Total', 'USER_Hour', 'USER_Ped_West', 'USER_Ped_East', 'USER_Ped_South', 'USER_Ped_North', 'USER_PDF_Name', 'Shape', 'ObjectID']
FC_fields = [f.name for f in arcpy.ListFields(turning_movement_count)]
fields_to_delete = list(set(FC_fields) - set(keep_list))
print(FC_fields)
print('DROP FIELDS : '+str(fields_to_delete))
arcpy.DeleteField_management(turning_movement_count, fields_to_delete)

print("----------%s seconds to run----------" % (time.time()-start_time))