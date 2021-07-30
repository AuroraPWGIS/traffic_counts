import pdfplumber, os, arcpy
import pandas as pd
from datetime import datetime

start_time = datetime.now()
arcpy.env.overwriteOutput = True
pd.set_option("display.max_columns", None)

#Variables
ADT_Class_Folder='C:/GIS_Processing/TrafficCounts/FullTrafficSignalCopy/ATD Class/'
test_csv = 'C:/GIS_Processing/TrafficCounts/FullTrafficSignalCopy/test_class.csv'
aurora_address_composite = "N:/PWD/Sidewalk Ice and Drainage Complaints/GIS/AuroraAddressComposite"
traffic_count_folder = 'C:/GIS_Processing/TrafficCounts/FullTrafficSignalCopy/ATD Class'
traf_count_folder_list = os.listdir(traffic_count_folder)
AADT_class = 'C:/GIS_Processing/TrafficCounts/temp_GDB.gdb/traffic_count_classification'

#Lists
filter_list = ['CLASS', ' SAT', ' WD', '.pdf', 'VOL']
direction_list = ['N.O.','S.O.','W.O.','E.O.']
intersection_list = []
aadt_list = []
direct_list = []
column_names = ['Address','Direction','Bikes', 'Cars_and_Trailers', '2_Axle_Long', 'Buses', '2_Axle_6_Tire', '3_Axle_Single', '4_Axle_Single', 'Less_Than_5_Axle_Double', '5_Axle_Double', 'More_Than_6_Axle_Double', 'Less_Than_6_Axle_Multi', '6_Axle_Multi', 'More_Than_6_Axle_Multi','Total']
keep_list = ['ObjectID', 'Shape', 'USER_Address','USER_Direction','USER_Bikes', 'USER_Cars_and_Trailers', 'USER_2_Axle_Long', 'USER_Buses', 'USER_2_Axle_6_Tire', 'USER_3_Axle_Single', 'USER_4_Axle_Single', 'USER_Less_Than_5_Axle_Double', 'USER_5_Axle_Double', 'USER_More_Than_6_Axle_Double', 'USER_Less_Than_6_Axle_Multi', 'USER_6_Axle_Multi', 'USER_More_Than_6_Axle_Multi','USER_Total']

#Set up dataframe with column names list
df = pd.DataFrame(columns = column_names)

#Reading each table in PDF, selecting desired row, making the PDF title geocode-able
for file in traf_count_folder_list:
    pdf_file = ADT_Class_Folder+file
    with pdfplumber.open(pdf_file) as pdf:
        pg_num = 0
        while pg_num <= 4:
            try:
                page = pdf.pages[pg_num]
                pg_num += 1
                text = (page.extract_text())
                for f in filter_list:
                    if f in file:
                        file = file.replace(f, '')
                for d in direction_list:
                    if d in file:
                        direct = d
                        file = file.replace(d, '&')
                text=((text.split('Day'))[1].split('Total')[0])
                text_list = text.split(' ')
                new_text_list = [s.replace('\n','') for s in text_list]
                new_text_list.insert(0,direct)
                new_text_list.insert(0,file)
                df_length = len(df)
                df.loc[df_length] = new_text_list
            except Exception:
                pg_num += 1
print(df)

#Pandas dataframe is exported to csv
df.to_csv(test_csv, index=False)

#Geocoding from an address locator on the N drive and the 'address' field created from the PDF name
arcpy.GeocodeAddresses_geocoding(test_csv, aurora_address_composite, "'Single Line Input' Address VISIBLE NONE", AADT_class, "STATIC")
print('Intersections geocoded')

#Field cleanup
FC_fields = [f.name for f in arcpy.ListFields(AADT_class)]
print(FC_fields)
fields_to_delete = list(set(FC_fields) - set(keep_list))
print('DROP FIELDS : '+str(fields_to_delete))
arcpy.DeleteField_management(AADT_class, fields_to_delete)

print ('Script took: '+str(datetime.now() - start_time))