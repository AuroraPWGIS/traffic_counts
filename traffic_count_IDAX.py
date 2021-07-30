import os, re, arcpy
from tabula import read_pdf
import pandas as pd
from datetime import datetime

start_time = time.time()

arcpy.env.OverwriteOutput = True
pd.set_option("display.max_columns", None)

#Variables
traffic_count_folder = 'C:/GIS_Processing/TrafficCounts/FullTrafficSignalCopy/IDAX'
test_csv = 'C:/GIS_Processing/TrafficCounts/FullTrafficSignalCopy/test_IDAX.csv'
aurora_address_composite = "N:/PWD/Sidewalk Ice and Drainage Complaints/GIS/AuroraAddressComposite"
folder = 'C:/GIS_Processing/TrafficCounts'
temp_GDB = 'C:/GIS_Processing/TrafficCounts/temp_GDB.gdb'
AADT_IDAX = 'C:/GIS_Processing/TrafficCounts/temp_GDB.gdb/traffic_count_midweek_average'
df_fin = pd.DataFrame()

#Lists
filter_list = [' CLASS', ' SAT', ' WD', '.pdf', ' VOL', '(2)']
direction_list = ['N.O.','S.O.','W.O.','E.O.']

#List all docs in folder
traf_count_folder_list = os.listdir(traffic_count_folder)

for i in traf_count_folder_list:
    df = read_pdf(traffic_count_folder+'/'+i, pages=1)
    for f in filter_list:
        if f in i:
            i = i.replace(f,'')
    for d in direction_list:
        if d in i:
            direc = d
            i = i.replace(d, '&')
    df = df[0]
    df = df.loc[df['Time'] == 'Total']
    df = df[['Unnamed: 18','Unnamed: 19', 'Unnamed: 20', 'Unnamed: 21', 'Unnamed: 22']]
    df['Unnamed: 18'] = df['Unnamed: 18'].replace(['-'], i)
    df['Unnamed: 19'] = df['Unnamed: 19'].replace(['-'], direc)
    df = df.rename(columns={'Unnamed: 18': 'Address', 'Unnamed: 19': 'Direction', 'Unnamed: 20': 'NB_OR_EB', 'Unnamed: 21': 'SB_OR_WB', 'Unnamed: 22': 'Total'})
    df_fin = pd.concat([df, df_fin], ignore_index=False)

#Dataframe transformation to CSV
df_fin.to_csv(test_csv, index=False)
print('Dataframe to csv')

#Check to see if FC exists - won't overwrite for some reason
if arcpy.Exists(AADT_IDAX):
    arcpy.Delete_management(AADT_IDAX)

#CSV geocode against composite address locator
arcpy.GeocodeAddresses_geocoding(test_csv, aurora_address_composite, "'Single Line Input' Address VISIBLE NONE", AADT_IDAX, "STATIC")
print('Intersections geocoded')

#Field cleanup work
keep_list=['USER_Address','USER_Direction','USER_NB_OR_EB', 'USER_SB_OR_WB', 'USER_Total', 'ObjectID', 'Shape']

FC_fields = [f.name for f in arcpy.ListFields(AADT_IDAX)]
fields_to_delete = list(set(FC_fields) - set(keep_list))
print('DROP FIELDS : '+str(fields_to_delete))
arcpy.DeleteField_management(AADT_IDAX, fields_to_delete)

print ('Script took: '+str(datetime.now() - start_time))