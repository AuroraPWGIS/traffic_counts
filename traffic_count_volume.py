import pdfplumber, os, arcpy
import pandas as pd
from datetime import datetime

start_time = datetime.now()
arcpy.env.overwriteOutput = True

#Variables
test_file = 'C:/GIS_Processing/TrafficCounts/FullTrafficSignalCopy/ATD Vol/2VOL - KINGSTON ST S.O. E 25TH DR.pdf'
test_csv = 'C:/GIS_Processing/TrafficCounts/FullTrafficSignalCopy/test_vol.csv'
aurora_address_composite = "N:/PWD/Sidewalk Ice and Drainage Complaints/GIS/AuroraAddressComposite"
keyword = 'AADT'
traffic_count_folder = 'C:/GIS_Processing/TrafficCounts/FullTrafficSignalCopy/ATD Vol'
traf_count_folder_list = os.listdir(traffic_count_folder)
AADT_vol = 'C:/GIS_Processing/TrafficCounts/temp_GDB.gdb/traffic_count_AADT'

#Lists
filter_list = [' VOL', ' SAT', ' WD', '.pdf' , '(2)']
direction_list = ['N.O.','S.O.','W.O.','E.O.']
intersection_list = []
aadt_list = []
direct_list = []
df = pd.DataFrame()

#read all text in pdfs and extract
for file in traf_count_folder_list:
    pdf_file = traffic_count_folder+'/'+file
    for f in filter_list:
        if f in file:
            file = file.replace(f, '')
    for d in direction_list:
        if d in file:
            direct = d
            file = file.replace(d, '&')
    with pdfplumber.open(pdf_file) as pdf:
        pg_num = 0
        page = pdf.pages[pg_num]
        text = (page.extract_text())
        while 'AADT' not in text:
            pg_num += 1
            page = pdf.pages[pg_num]
            text = (page.extract_text())
        else:
            before_keyword, keyword, after_keyword= text.partition(keyword)
            intersection_list.append(file)
            aadt_list.append(after_keyword)
            direct_list.append(direct)
            print(file + ' ' + direct + ' ' + after_keyword)
df['Address'] = intersection_list
df['AADT'] = aadt_list
df['Direction'] = direct_list
df.to_csv(test_csv,index = False)

#Geocoding
arcpy.GeocodeAddresses_geocoding(test_csv, aurora_address_composite, "'Single Line Input' Address VISIBLE NONE", AADT_vol, "STATIC")
print('Intersections geocoded')

#Field cleanup work
keep_list=['USER_Address','USER_AADT','USER_Direction','ObjectID','Shape']
FC_fields = [f.name for f in arcpy.ListFields(AADT_vol)]
fields_to_delete = list(set(FC_fields) - set(keep_list))
print('DROP FIELDS : '+str(fields_to_delete))
arcpy.DeleteField_management(AADT_vol, fields_to_delete)

print ('Script took: '+str(datetime.now() - start_time))