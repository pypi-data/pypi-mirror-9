"""test flow dir"""
import pygeoprocessing.routing
import pygeoprocessing.geoprocessing

dem_uri = r"C:\Users\rich\Documents\delete_clinton_sdr\prepared_data\aligned_dem.tif"
flow_direction_uri = r"C:\Users\rich\Documents\delete_flow_dir.tif"
flow_accumulation_uri = r"C:\Users\rich\Documents\flow_accumulation.tif"
pygeoprocessing.routing.flow_direction_d_inf(dem_uri, flow_direction_uri)
pygeoprocessing.routing.flow_accumulation(
    flow_direction_uri, dem_uri, flow_accumulation_uri)


