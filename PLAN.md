# Tableau to Power BI Migration Plan

This document outlines the automated strategy for migrating Tableau reports (.twbx/.twb) to Power BI (.pbip/.pbix).

## Goal
Achieve 90-100% accuracy in migrating calculations, visuals, measures, filters, and layouts programmatically.

## Architecture

### Phase 1: Metadata Extraction
- **Input**: `.twbx` (zipped) or `.twb` (XML).
- **Process**:
    - Unzip `.twbx` to retrieve the `.twb` XML.
    - Parse XML to extract:
        - Data sources and connection metadata.
        - Calculated fields (Tableau formulas).
        - Worksheet definitions (Visual types, field mappings).
        - Dashboard layouts (Zones, sizes, positions).
- **Tool**: `migration_tool/tableau_extractor.py`

### Phase 2: Translation & Mapping
- **Process**:
    - **Logic**: Translate Tableau formulas (e.g., LODs like `FIXED`, `ATTR`) into DAX measures.
    - **Visuals**: Map Tableau visual types to Power BI equivalents (PBIR format).
    - **Fields**: Map Tableau dimensions/measures to Power BI model columns.
- **Tool**: `migration_tool/pbi_generator.py` (Translation logic)

### Phase 3: PBIP Template Generation
- **Input**: A "Sample" `.pbip` folder providing the base theme and semantic model.
- **Process**:
    - Clone the sample `.pbip` structure.
    - Inject translated DAX measures into `model.bim` or `TMDL` files.
    - Programmatically generate `visual.pbir` files for each Tableau worksheet.
    - Update dashboard layout files.
- **Tool**: `migration_tool/pbi_generator.py`

### Phase 4: Package & Deploy
- **Process**:
    - Compress the generated `.pbip` folder into a `.pbix` file.
    - **Upload**: Use Power BI REST API `POST /imports` to upload the report.
    - **Rebind**: Use Power BI REST API `POST /reports/{id}/Rebind` to connect the report to the target semantic model.
- **Tool**: `migration_tool/pbi_deployer.py` and `migration_tool/main.py`

## Implementation Status
- [x] Basic Tableau Extractor (XML parsing)
- [x] Basic PBIP Generator (Folder cloning, model injection placeholder)
- [x] Basic PBI Deployer (REST API authentication, Upload, Rebind)
- [ ] Advanced Tableau-to-DAX Translation logic
- [ ] PBIR Visual generation logic
- [ ] Packaging (PBIP to PBIX) logic

## Next Steps
1. Analyze the provided sample `.pbip` to understand the target schema (TMDL vs model.bim).
2. Analyze the sample `.twbx` to refine the extraction logic.
3. Implement the visual mapping to PBIR.
