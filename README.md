# Global_SSPs_Clip
The second model in the workflow designed to crop global ssp datasets to a specific country.
This model takes the global ssp datasets and crops the data to the country of interest.
The raster data is then aggregated to the local authority level and a gpkg file is produced.
This shows the population change per LAD for future projections.

## Description
Global datasets are cropped according to the location selected by the user and aggregated to the LAD level.

## Input Files (data slots)
* Boundary File
  * Description: A .gpkg file containing the boundary of the country of interest.
  * Location: /data/inputs/boundary
* SSP Data Sets
  * Description: A zip file with the relevent global ssp data.
  * Location: /data/inputs/ssp
* Local Authority Districts
  * Description: A .gpkg file containing the boundarys for each Local Authority District.
  * Location: /data/inputs/lads
* Parameters
  * Description: A .csv file detailing the selected parameters - taken from the preceeding Global_SSPS:Inputs model.
  * Location: /data/inputs/parameters

## Outputs
* SSP Results
  * Description: Contains three single .gpkg files detailing projected changes in popualtion, urban and rural land form for the selected local authority areas.
  * Location: /data/outputs/
* Parameters
  * Description: All parameters and their values are stored in a csv file.
  * Location: /data/outputs/parameters
