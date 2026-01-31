import zipfile
import os
import xml.etree.ElementTree as ET
import json

class TableauExtractor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.twb_content = None
        self.metadata = {
            "data_sources": [],
            "calculations": [],
            "worksheets": [],
            "dashboards": []
        }

    def extract_twb(self):
        """Extracts the .twb file from a .twbx (zip) or reads .twb directly."""
        if self.file_path.endswith('.twbx'):
            with zipfile.ZipFile(self.file_path, 'r') as zip_ref:
                # Find the .twb file inside
                twb_files = [f for f in zip_ref.namelist() if f.endswith('.twb')]
                if not twb_files:
                    raise FileNotFoundError("No .twb file found in .twbx")
                with zip_ref.open(twb_files[0]) as f:
                    self.twb_content = f.read()
        elif self.file_path.endswith('.twb'):
            with open(self.file_path, 'rb') as f:
                self.twb_content = f.read()
        else:
            raise ValueError("Unsupported file format. Use .twb or .twbx")

    def parse_twb(self):
        """Parses the XML content of the .twb file."""
        if not self.twb_content:
            self.extract_twb()
        
        root = ET.fromstring(self.twb_content)
        
        # 1. Extract Data Sources and Calculations
        for ds in root.findall('.//datasource'):
            name = ds.get('name', ds.get('caption', 'Unknown'))
            source_meta = {
                "name": name,
                "caption": ds.get('caption'),
                "columns": []
            }
            
            # Extract calculations
            for col in ds.findall('.//column'):
                calc = col.find('calculation')
                if calc is not None:
                    self.metadata["calculations"].append({
                        "datasource": name,
                        "name": col.get('name'),
                        "caption": col.get('caption'),
                        "formula": calc.get('formula'),
                        "datatype": col.get('datatype')
                    })
                else:
                    source_meta["columns"].append({
                        "name": col.get('name'),
                        "caption": col.get('caption'),
                        "datatype": col.get('datatype'),
                        "role": col.get('role')
                    })
            self.metadata["data_sources"].append(source_meta)

        # 2. Extract Worksheets (Visuals)
        for ws in root.findall('.//worksheet'):
            ws_meta = {
                "name": ws.get('name'),
                "visual_type": "unknown", # Needs deeper parsing of 'panes'
                "dimensions": [],
                "measures": [],
                "filters": []
            }
            
            # Extract columns/rows (dimensions/measures)
            for shelf in ws.findall('.//shelf'):
                shelf_name = shelf.get('name')
                if shelf_name in ['columns', 'rows']:
                    for enc in shelf.findall('.//enc'):
                        ws_meta[shelf_name] = ws_meta.get(shelf_name, [])
                        ws_meta[shelf_name].append(enc.get('column'))

            # Extract Filters
            for filter_node in ws.findall('.//filter'):
                ws_meta["filters"].append({
                    "column": filter_node.get('column'),
                    "class": filter_node.get('class')
                })
                
            self.metadata["worksheets"].append(ws_meta)

        # 3. Extract Dashboards
        for db in root.findall('.//dashboard'):
            db_meta = {
                "name": db.get('name'),
                "zones": []
            }
            # Zones contain the layout information
            for zone in db.findall('.//zone'):
                db_meta["zones"].append({
                    "name": zone.get('name'),
                    "type": zone.get('type'),
                    "x": zone.get('x'),
                    "y": zone.get('y'),
                    "width": zone.get('w'),
                    "height": zone.get('h')
                })
            self.metadata["dashboards"].append(db_meta)

        return self.metadata

    def save_metadata(self, output_path):
        with open(output_path, 'w') as f:
            json.dump(self.metadata, f, indent=4)

if __name__ == "__main__":
    print("Tableau Extractor logic ready.")
