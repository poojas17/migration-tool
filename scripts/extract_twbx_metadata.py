import os
import xml.etree.ElementTree as ET
import pandas as pd

TW B_PATH = os.path.join('twbx','extracted','ExecutiveKPI.twb')
EXTRACTED_DIR = os.path.join('twbx','extracted')
OUT_XLSX = os.path.join('twbx','ExecutiveKPI_metadata.xlsx')

root = ET.parse(TWB_PATH).getroot()

# Workbook info
wb_info = {
    'original-version': root.attrib.get('original-version',''),
    'version': root.attrib.get('version',''),
    'source-build': root.attrib.get('source-build',''),
    'source-platform': root.attrib.get('source-platform','')
}

# Datasources
ds_rows = []
for ds in root.findall('.//datasource'):
    ds_rows.append({
        'name': ds.attrib.get('name',''),
        'caption': ds.attrib.get('caption',''),
        'inline': ds.attrib.get('inline',''),
        'version': ds.attrib.get('version','')
    })

# Connections (global search)
conn_rows = []
for conn in root.findall('.//connection'):
    row = conn.attrib.copy()
    # map nested named-connections filenames if present
    nc = conn.find('.//named-connections')
    if nc is not None:
        files = []
        for n in nc.findall('.//connection'):
            fn = n.attrib.get('filename')
            if fn:
                files.append(fn)
        row['named_filenames'] = ';'.join(files)
    conn_rows.append(row)

# Parameters: look for datasource named 'Parameters'
param_rows = []
for ds in root.findall('.//datasource'):
    if ds.attrib.get('name','').lower() == 'parameters':
        for col in ds.findall('.//column'):
            param_rows.append({
                'caption': col.attrib.get('caption',''),
                'name': col.attrib.get('name',''),
                'datatype': col.attrib.get('datatype',''),
                'value': col.attrib.get('value','')
            })

# Worksheets and dashboards
worksheets = [w.attrib.get('name','') for w in root.findall('.//worksheet')]
dashboards = [d.attrib.get('name','') for d in root.findall('.//dashboard')]

# Image assets and Data files
images = []
images_dir = os.path.join(EXTRACTED_DIR,'Image')
if os.path.isdir(images_dir):
    images = sorted(os.listdir(images_dir))

data_files = []
data_dir = os.path.join(EXTRACTED_DIR,'Data')
for rootd, dirs, files in os.walk(data_dir):
    for f in files:
        data_files.append(os.path.join(rootd,f))

# Columns inside relations
col_rows = []
for relation in root.findall('.//relation'):
    rname = relation.attrib.get('name','')
    for col in relation.findall('.//column'):
        col_rows.append({
            'relation': rname,
            'column_name': col.attrib.get('name',''),
            'datatype': col.attrib.get('datatype',''),
            'ordinal': col.attrib.get('ordinal','')
        })

# Create DataFrames
df_wb = pd.DataFrame([wb_info])
df_ds = pd.DataFrame(ds_rows)
df_conn = pd.DataFrame(conn_rows)
df_params = pd.DataFrame(param_rows)
df_ws = pd.DataFrame({'worksheet':worksheets})
df_dash = pd.DataFrame({'dashboard':dashboards})
df_images = pd.DataFrame({'image':images})
df_datafiles = pd.DataFrame({'datafile':data_files})
df_cols = pd.DataFrame(col_rows)

# Write to Excel
with pd.ExcelWriter(OUT_XLSX, engine='openpyxl') as writer:
    df_wb.to_excel(writer, sheet_name='Summary', index=False)
    df_ds.to_excel(writer, sheet_name='Datasources', index=False)
    df_conn.to_excel(writer, sheet_name='Connections', index=False)
    df_params.to_excel(writer, sheet_name='Parameters', index=False)
    df_ws.to_excel(writer, sheet_name='Worksheets', index=False)
    df_dash.to_excel(writer, sheet_name='Dashboards', index=False)
    df_images.to_excel(writer, sheet_name='Images', index=False)
    df_datafiles.to_excel(writer, sheet_name='DataFiles', index=False)
    df_cols.to_excel(writer, sheet_name='RelationColumns', index=False)

print(f"Saved workbook metadata to {OUT_XLSX}")
