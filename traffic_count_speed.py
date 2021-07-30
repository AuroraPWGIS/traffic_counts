import pdfplumber, os, arcpy, re
import pandas as pd
from datetime import datetime

start_time = datetime.now()
arcpy.env.overwriteOutput = True

#Variables
traffic_count_folder = 'C:/GIS_Processing/TrafficCounts/FullTrafficSignalCopy/ATD Speed'
speed_csv = 'C:/GIS_Processing/TrafficCounts/FullTrafficSignalCopy/traffic_count_speed.csv'
aurora_address_composite = "N:/PWD/Sidewalk Ice and Drainage Complaints/GIS/AuroraAddressComposite"
traffic_count_speed = 'C:/GIS_Processing/TrafficCounts/temp_GDB.gdb/traffic_count_speed'
direction_list = ['NB', 'SB', 'WB', 'EB']
filter_list = [' WD',' SPEED',' SAT', '.pdf', '(2)']
directional_list = ['N.O.','S.O.','W.O.','E.O.']
keep_list = ['ObjectID', 'Shape','USER_Address', 'USER_Direction', 'USER_Direction_Travel', 'USER_1_15','USER_16_20','USER_21_25', 'USER_26_30', 'USER_31_35', 'USER_36_40', 'USER_41_45', 'USER_46_50', 'USER_51_55', 'USER_56_60', 'USER_61_65', 'USER_66_70', 'USER_71_75', 'USER_76_999', 'USER_Total']
traffic_count_speed = 'C:/GIS_Processing/TrafficCounts/temp_GDB.gdb/traffic_count_speed'
df_column_names = ['Address', 'Direction', 'Direction_Travel', '1_15','16_20','21_25', '26_30', '31_35', '36_40', '41_45', '46_50', '51_55', '56_60', '61_65', '66_70', '71_75', '76_999', 'Total']
df = pd.DataFrame(columns = df_column_names)
test_list = []

traf_count_folder_list = os.listdir(traffic_count_folder)

for file in traf_count_folder_list:
    pdf_file = traffic_count_folder+'/'+file
    with pdfplumber.open(pdf_file) as pdf:
        pg_num = 0
        total_pages = (len(pdf.pages))
        while pg_num < total_pages:
            page = pdf.pages[pg_num]
            text = (page.extract_text())
            for f in filter_list:
                if f in file:
                    file = file.replace(f,'')
            for dir in directional_list:
                if dir in file:
                    direc = dir
                    file = file.replace(dir,'&')
            for d in direction_list:
                if d in text:
                    direct = d
                    print (direct)
            if 'Total' in text:
                try:
                    pg_num += 1
                    text_list = []
                    text = text.replace('Total','Sum',1)
                    text = text.split('Total')[1].split('Percent')[0]
                    text_list = text.split(' ')
                    if len(text_list) == 20:
                        text_list.pop(0)
                        text_list = (text_list[:-4])
                        text_list.insert(0, direct)
                        text_list.insert(0, direc)
                        text_list.insert(0, file)
                        series = pd.Series(text_list, index = df.columns)
                        df = df.append(series, ignore_index = True)
                except Exception:
                    print('this page is not relevant - '+ pdf_file)
            else:
                pg_num += 1
                print('No Keywords were found')

print(df)
df.to_csv(speed_csv,index = False)

#Geocoding
arcpy.GeocodeAddresses_geocoding(speed_csv, aurora_address_composite, "'Single Line Input' Address VISIBLE NONE", traffic_count_speed, "STATIC")
print('Intersections geocoded')

#Field cleanup work
FC_fields = [f.name for f in arcpy.ListFields(traffic_count_speed)]
print(FC_fields)
fields_to_delete = list(set(FC_fields) - set(keep_list))
print('DROP FIELDS : '+str(fields_to_delete))
arcpy.DeleteField_management(traffic_count_speed, fields_to_delete)

print ('Script took: '+str(datetime.now() - start_time))