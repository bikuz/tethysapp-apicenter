import datetime
import os, tempfile, shutil, functools
import requests
import csv
import json
import calendar
import netCDF4
from netCDF4 import Dataset

import numpy as np
import shapely.geometry
import xml.etree.ElementTree as ET
from osgeo import gdal
import rasterio as rio
import rasterstats as rstats
from .config import *
from django.http import JsonResponse, HttpResponse


# from tethys_sdk.workspaces import app_workspace

def get_pt_values(s_var, geom_data, interval, path):
    # Empty list to store the timeseries values
    ts_plot = []
    json_obj = {}

    # Defining the lat and lon from the coords string
    coords = geom_data.split(',')
    stn_lat = float(coords[1])
    stn_lon = float(coords[0])
    nc_files = get_hiwat_file(path)
    nc_file = nc_files[interval]

    nc_fid = Dataset(nc_file, 'r')  # Reading the netCDF file
    lis_var = nc_fid.variables
    lats = nc_fid.variables['latitude'][:]  # Defining the latitude array
    lons = nc_fid.variables['longitude'][:]  # Defining the longitude array
    field = nc_fid.variables[s_var][:]  # Defning the variable array
    time = nc_fid.variables['time'][:]

    abslat = np.abs(lats - stn_lat)  # Finding the absolute latitude
    abslon = np.abs(lons - stn_lon)  # Finding the absolute longitude

    lat_idx = (abslat.argmin())
    lon_idx = (abslon.argmin())

    if interval == 'det':
        for timestep, v in enumerate(time):
            val = field[timestep, lat_idx, lon_idx]
            time_stamp = time[timestep] * 1000
            ts_plot.append([time_stamp, float(val)])
            ts_plot.sort()

    if interval == 'hourly':
        for timestep, v in enumerate(time):
            val = field[timestep, lat_idx, lon_idx]
            dt_str = netCDF4.num2date(lis_var['time'][timestep], units=lis_var['time'].units,
                                      calendar=lis_var['time'].calendar)
            dt_str = datetime.datetime.fromisoformat(str(dt_str))
            # dt_str = datetime.datetime.strftime(dt_str, '%Y_%m_%d_%H_%M')
            time_stamp = calendar.timegm(dt_str.utctimetuple()) * 1000
            # time_stamp = time[timestep] * 1000
            ts_plot.append([time_stamp, float(val)])
            ts_plot.sort()

    if interval == 'day1' or interval == 'day2':
        val = field[0, lat_idx, lon_idx]
        dt_str = netCDF4.num2date(lis_var['time'][0], units=lis_var['time'].units,
                                  calendar=lis_var['time'].calendar)
        dt_str = datetime.datetime.fromisoformat(str(dt_str))
        # dt_str = datetime.datetime.strftime(dt_str, '%Y_%m_%d_%H_%M')
        time_stamp = calendar.timegm(dt_str.utctimetuple()) * 1000
        ts_plot.append([time_stamp, float(val)])
        ts_plot.sort()

    # Returning the list with the timeseries values and the point so that they can be displayed on the graph.
    point = [round(stn_lat, 2), round(stn_lon, 2)]
    json_obj["plot"] = ts_plot
    json_obj["geom"] = point
    return json_obj


def get_poylgon_values(s_var, geom_data, interval, path,returnType):
    # Empty list to store the timeseries values
    ts_plot = []
    json_obj = {}

    # Defining the lat and lon from the coords string
    # poly_geojson = json.load(geom_data)
    shape_obj = shapely.geometry.shape(geom_data)
    bounds = shape_obj.bounds

    miny = float(bounds[1])
    minx = float(bounds[0])
    maxx = float(bounds[2])
    maxy = float(bounds[3])

    nc_files = get_hiwat_file(path)
    nc_file = nc_files[interval]

    nc_fid = Dataset(nc_file, 'r')  # Reading the netCDF file
    lis_var = nc_fid.variables
    lats = nc_fid.variables['latitude'][:]  # Defining the latitude array
    lons = nc_fid.variables['longitude'][:]  # Defining the longitude array
    field = nc_fid.variables[s_var][:]  # Defning the variable array
    time = nc_fid.variables['time'][:]
    abslat = np.abs(lats - miny)
    abslon = np.abs(lons - minx)
    abslat2 = np.abs(lats - maxy)
    abslon2 = np.abs(lons - maxx)
    lon_idx = (abslat.argmin())
    lat_idx = (abslon.argmin())
    lon2_idx = (abslat2.argmin())
    lat2_idx = (abslon2.argmin())

    deltaLats = lats[1] - lats[0]
    deltaLons = lons[1] - lons[0]

    deltaLatsAbs = np.abs(deltaLats)
    deltaLonsAbs = np.abs(deltaLons)
    geotransform = rio.transform.from_origin(lons.min(), lats.max(), deltaLatsAbs, deltaLonsAbs)

    #
    # lat_idx = (abslat.argmin())
    # lon_idx = (abslon.argmin())
    #
    if interval == 'det':
        for timestep, v in enumerate(time):
            nc_arr = field[timestep]
            nc_arr[nc_arr > 9000] = np.nan  # use the comparator to drop nodata fills
            if deltaLats > 0:
                nc_arr = nc_arr[::-1]  # vertically flip array so tiff orientation is right (you just have to, try it)
            tt = rstats.zonal_stats(geom_data, nc_arr, affine=geotransform,
                                    stats=['min', 'max', 'mean', 'std', 'median'])
            val = tt[0]['mean']

            # vals = field[timestep,lat_idx:lat2_idx, lon_idx:lon2_idx]
            # val = np.mean(vals)
            # if math.isnan(float(val)):
            #     val = None
            time_stamp = time[timestep] * 1000
            ts_plot.append([time_stamp, val])
            ts_plot.sort()

    if interval == 'hourly':
        if returnType=='CSV':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="requestedData.csv"'
            header = ['DateTime', 'mean', 'min', 'max', 'std', 'median']
            writer = csv.writer(response)
            writer.writerow(header)
        else:
            json_obj={
                'mean':[],
                'min':[],
                'max':[],
                'std':[],
                'median':[]
            }
        for timestep, v in enumerate(time):
            nc_arr = field[timestep]
            nc_arr[nc_arr > 9000] = np.nan  # use the comparator to drop nodata fills
            if deltaLats > 0:
                nc_arr = nc_arr[::-1]  # vertically flip array so tiff orientation is right (you just have to, try it)
            tt = rstats.zonal_stats(geom_data, nc_arr, affine=geotransform,
                                    stats=['min', 'max', 'mean', 'std', 'median'])
            # val=tt[0]['mean']
            interestedmean = round(tt[0]['mean'], 4)
            interestedMin = round(tt[0]['min'], 4)
            interestedMax = round(tt[0]['max'], 4)
            interestedSTD = round(tt[0]['std'], 4)
            interestedMed = round(tt[0]['median'], 4)
            dt_str = netCDF4.num2date(lis_var['time'][timestep], units=lis_var['time'].units,
                                      calendar=lis_var['time'].calendar)
            dt_str = datetime.datetime.fromisoformat(str(dt_str))
            dt_str = str(datetime.datetime.strftime(dt_str, '%Y/%m/%d %H:%M'))

            if returnType=='CSV':
                writer.writerow([dt_str, interestedmean, interestedMin, interestedMax, interestedSTD, interestedMed])

            else:
                json_obj['mean'].append([dt_str,interestedmean])
                json_obj['min'].append([dt_str,interestedMin])
                json_obj['max'].append([dt_str,interestedMax])
                json_obj['std'].append([dt_str,interestedSTD])
                json_obj['median'].append([dt_str,interestedMed])

        if returnType == 'CSV':
            return response
        else:
            return json_obj
        

        #     dt_str = netCDF4.num2date(lis_var['time'][timestep], units=lis_var['time'].units,
        #                               calendar=lis_var['time'].calendar)
        #     dt_str = datetime.datetime.fromisoformat(str(dt_str))
        #     # dt_str = datetime.datetime.strftime(dt_str, '%Y_%m_%d_%H_%M')
        #     time_stamp = calendar.timegm(dt_str.utctimetuple()) * 1000
        #     # time_stamp = time[timestep] * 1000
        #     ts_plot.append([time_stamp, interestedmean, interestedMin, interestedMax, interestedSTD, interestedMed])
        # ts_plot.sort()

    if interval == 'day1' or interval == 'day2':
        nc_arr = field[timestep]
        nc_arr[nc_arr > 9000] = np.nan  # use the comparator to drop nodata fills
        if deltaLats > 0:
            nc_arr = nc_arr[::-1]  # vertically flip array so tiff orientation is right (you just have to, try it)
        tt = rstats.zonal_stats(geom_data, nc_arr, affine=geotransform, stats='mean')
        val = tt[0]['mean']

        # vals = field[0, lat_idx:lat2_idx, lon_idx:lon2_idx]
        #
        # val = np.mean(vals)
        # if math.isnan(float(val)):
        #     val=None
        dt_str = netCDF4.num2date(lis_var['time'][0], units=lis_var['time'].units,
                                  calendar=lis_var['time'].calendar)

        dt_str = datetime.datetime.fromisoformat(str(dt_str))
        # dt_str = datetime.datetime.strftime(dt_str, '%Y_%m_%d_%H_%M')
        time_stamp = calendar.timegm(dt_str.utctimetuple()) * 1000
        ts_plot.append([time_stamp, val])
        ts_plot.sort()

    geom = [round(minx, 2), round(miny, 2), round(maxx, 2), round(maxy, 2)]

    json_obj["plot"] = ts_plot
    json_obj["geom"] = geom

    return json_obj


# get_pt_values('TMP_2maboveground','91.1,20.7')
def generate_variables_meta():
    db_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'workspaces/app_workspace/data/var_info.txt')
    variable_list = []
    var_issues = []
    with open(db_file, mode='r') as f:
        f.readline()  # Skip first line

        lines = f.readlines()

    for line in lines:
        if line != '':
            line = line.strip()
            linevals = line.split('|')
            variable_id = linevals[0]
            category = linevals[1]
            display_name = linevals[2]
            units = linevals[3]
            vmin = linevals[4]
            vmax = linevals[5]
            start = linevals[6]
            end = linevals[7]

            try:
                # print variable_id.lower()
                # colors_list = retrieve_colors(str(variable_id).lower())
                # scale = calc_color_range(float(vmin), float(vmax),len(colors_list))
                variable_list.append({
                    'id': variable_id,
                    'category': category,
                    'display_name': display_name,
                    'units': units,
                    'min': vmin,
                    'max': vmax,
                    'start': start,
                    'end': end
                    # 'scale': scale,
                    # 'colors_list':colors_list
                })
            except Exception as e:
                # print variable_id,e
                var_issues.append(variable_id)
                scale = calc_color_range(float(vmin), float(vmax), 20)
                variable_list.append({
                    'id': variable_id,
                    'category': category,
                    'display_name': display_name,
                    'units': units,
                    'min': vmin,
                    'max': vmax,
                    'start': start,
                    'end': end,
                    'scale': scale
                })
                continue

    # print var_issues
    return variable_list


def calc_color_range(min, max, classes):
    # breaks = None

    if classes is not None:
        breaks = int(classes)
    else:
        breaks = int(20)

    interval = float(abs((max - min) / breaks))

    if interval == 0:
        scale = [0] * breaks
    else:
        scale = np.arange(min, max, interval).tolist()

    return scale


def get_thredds_info():
    catalog_url = THREDDS_catalog
    catalog_wms = THREDDS_wms
    urls_obj = {}
    if catalog_url[-1] != "/":
        catalog_url = catalog_url + '/'

    if catalog_wms[-1] != "/":
        catalog_wms = catalog_wms + '/'

    catalog_xml_url = catalog_url + 'catalog.xml'

    possible_dates = []
    valid_dates = []

    cat_response = requests.get(catalog_xml_url, verify=False)

    cat_tree = ET.fromstring(cat_response.content)

    for elem in cat_tree.iter():
        for k, v in list(elem.attrib.items()):
            if 'title' in k:
                # if 'title' in k and '2018' in v:
                possible_dates.append(v[:8])

    for date in possible_dates:
        try:
            valid_date = datetime.datetime.strptime(date, "%Y%m%d")
            valid_dates.append(valid_date)

        except Exception as e:
            print("this is error")
            print(date)
            continue

    latest_date = max(valid_dates).strftime("%Y%m%d12")

    date_xml_url = catalog_url + latest_date + '/catalog.xml'

    date_xml = requests.get(date_xml_url, verify=False)

    date_response = ET.fromstring(date_xml.content)

    for el in date_response.iter():
        for k, v in list(el.items()):
            if 'urlPath' in k:
                if 'Control' in v:
                    urls_obj['det'] = catalog_wms + v
                if 'hourly' in v:
                    urls_obj['hourly'] = catalog_wms + v
                if 'day1' in v:
                    urls_obj['day1'] = catalog_wms + v
                if 'day2' in v:
                    urls_obj['day2'] = catalog_wms + v

    return urls_obj


def get_hiwat_file(path):
    hiwat_files = {}
    if path == 'None':
        latest_dir = max([os.path.join(HIWAT_storage, d) for d in os.listdir(HIWAT_storage) if
                          os.path.isdir(os.path.join(HIWAT_storage, d)) if 'allhourly' not in d if
                          'RAPID_OUTPUT' not in d])
    else:
        latest_dir = path

    print(latest_dir)
    # print(latest_dir)
    for file in os.listdir(latest_dir):
        if 'hourly' in file:
            hiwat_files['hourly'] = os.path.join(latest_dir, file)
        if 'Control' in file:
            hiwat_files['det'] = os.path.join(latest_dir, file)
        # if 'day1' in file:
        #     hiwat_files['day1'] = os.path.join(latest_dir, file)
        # if 'day2' in file:
        #     hiwat_files['day2'] = os.path.join(latest_dir, file)

    return hiwat_files








