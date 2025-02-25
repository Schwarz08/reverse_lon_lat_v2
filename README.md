# reverse_lon_lat_v2
## Input:
### All input variables can be found under main.
### rf_db_file_path: RF database file path
### rf_db_sheet_name: RF database sheet name
### coverage_width: coverage width per sector
### coverage_radius: coverage radius per sector
### n_samples: how many geographic points to query per sector
### delay: api query delay
### address_type_classification.xlsx: Excel file containing the importance thresholds of each Nomatim address type
## Output:
### coverage_db_summary.csv: summary of api query results per sector. result is the most important place and road for each sector.
