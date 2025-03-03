# reverse_lon_lat_v2
## Input:
### All input variables can be found under main.
* rf_db_file_path: RF database file path
* rf_db_sheet_name: RF database sheet name
* coverage_width: Coverage width per sector
* coverage_radius: Coverage radius per sector
* n_samples: Geographic points to query per sector
* delay: API query delay
* address_type_classification.xlsx: Excel file containing the importance thresholds of each Nomatim address type
## Output:
* coverage_db_summary.csv: Summary of API query results per sector. The results are the most important place and road for each sector.
