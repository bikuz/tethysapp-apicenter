from http import HTTPStatus
from django.http import JsonResponse, HttpResponse
import datetime as dt
import psycopg2, json,decimal, datetime, csv
from rest_framework.authentication import TokenAuthentication,SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes
import scipy.stats as sp
import numpy as np
from datetime import timedelta
from .utils import get_pt_values,get_poylgon_values
from .config import *
from tethys_sdk.workspaces import app_workspace
import os.path
import shapely.geometry

# from rest_framework import

def getRecentDate(comid, cty):
    conn = psycopg2.connect(host="192.168.10.35", database="servirFloodHiwat", user="postgres", password="changeit2")
    cur = conn.cursor()
    query = 'select distinct(rundate) from forecast' + cty + ' where comid = ' + comid + ' order by rundate desc'

    try:
        cur.execute(query)
        a = cur.fetchall()
        bb = (str(a[0])[19:-3]).split(",")
        b = bb[0].strip() + "-" + "{:02d}".format(int(bb[1])) + "-" + "{:02d}".format(int(bb[2]))
    except:
        runDate = dt.datetime.now().date() - timedelta(1)
        b = runDate.strftime('%Y-%m-%d')
    finally:
        conn.close()
    return b

# @login_required()
@api_view(['GET'])
@authentication_classes((TokenAuthentication, SessionAuthentication,))
def getFeaturesHIWAT(request):
    country =request.GET.get('cty')
    # country = "nepaRiver"
    json_obj = {}
    conn = psycopg2.connect(host="192.168.10.35", database="servirFloodHiwat", user="postgres", password="changeit2")
    cur = conn.cursor()
    feature_collection={}
    try:
        query = 'select comid, risk, riv_name, ST_AsGeoJSON(geom) AS geometry FROM public.river' + country
        cur.execute(query)
        rows = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        geomIndex = colnames.index("geometry")

        feature_collection = {'type': 'FeatureCollection', 'features': []}
        for row in rows:
            feature = {
                'type': 'Feature',
                'geometry': json.loads(row[geomIndex]),
                'properties': {},
            }
            for index, colname in enumerate(colnames):
                if colname not in ('geometry', 'geom'):
                    if isinstance(row[index], datetime.datetime):
                        value = str(row[index])
                    else:
                        value = row[index]
                    feature['properties'][colname] = value

            feature_collection['features'].append(feature)
        json_obj["feature"] = feature_collection
    finally:
        conn.close()
    return JsonResponse(feature_collection)
    # return json.dumps(feature_collection, indent=None, default=check_for_decimals)

# @login_required()
@api_view(['GET'])
@authentication_classes((TokenAuthentication, SessionAuthentication,))
def getFeaturesHIWATPA(request):
    country =request.GET.get('cty')
    # country = "nepaRiver"
    json_obj = {}
    conn = psycopg2.connect(host="192.168.10.35", database="servirFloodHiwat", user="postgres", password="changeit2")
    cur = conn.cursor()
    feature_collection = {}
    try:
        # query = 'select comid, risk, riv_name, ST_AsGeoJSON(geom) AS geometry FROM public.praticalActionRiver"'
        query = """ SELECT comid, risk, riv_name, ST_AsGeoJSON(geom) as geometry FROM public.rivernepal WHERE ST_Intersects(geom, (SELECT geom FROM public."pactionAction" where gn = '""" + country + """')) order by comid """
        cur.execute(query)
        rows = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        geomIndex = colnames.index("geometry")

        feature_collection = {'type': 'FeatureCollection', 'features': []}
        for row in rows:
            feature = {
                'type': 'Feature',
                'geometry': json.loads(row[geomIndex]),
                'properties': {},
            }
            for index, colname in enumerate(colnames):
                if colname not in ('geometry', 'geom'):
                    if isinstance(row[index], datetime.datetime):
                        value = str(row[index])
                    else:
                        value = row[index]
                    feature['properties'][colname] = value

            feature_collection['features'].append(feature)
        json_obj["feature"] = feature_collection
    finally:
        conn.close()
    return JsonResponse(feature_collection)
    # return json.dumps(feature_collection, indent=None, default=check_for_decimals)

@api_view(['GET'])
@authentication_classes((TokenAuthentication, SessionAuthentication,))
def getForecastHIWAT(request):
    comid = request.GET.get('comid')
    cty = request.GET.get('cty')
    completeDate=None
    try:
        completeDate=request.GET.get('completeDate')
    except:
        completeDate=None
    # runDate = dt.datetime.now().date() - timedelta(days=0)
    recentDate = getRecentDate(comid, cty)
    dates = []
    values = []
    return_obj = {}
    # print (runDate)
    conn = psycopg2.connect(host="192.168.10.35", database="servirFloodHiwat", user="postgres", password="changeit2")
    cur = conn.cursor()
    content={}
    try:
        query=None
        if(completeDate):
            query = "SELECT forecastdate, forecastvalue FROM public.forecast" + cty + completeDate + " where comid =" \
                + str(comid) + " and runDate = '" + str(recentDate) + "' order by forecastdate"
        else:
            query = "SELECT forecastdate, forecastvalue FROM public.forecast" + cty + " where comid =" \
                + str(comid) + " and runDate = '" + str(recentDate) + "' order by forecastdate"
        cur.execute(query)
        rows = cur.fetchall()
        for row in rows:
            # hres_dates.append(str(dt.datetime.strftime(row[0],'%Y-%m-%d %H:%M:%S')))
            # hres_values.append(row[1])

            # if 'nan' not in str(row[1]):
            # dates.append(str(dt.datetime.strftime(row[0],'%Y-%m-%d %H:%M:%S')))
            if cty.startswith('nep'):
                dates.append(str(str((row[0] + dt.timedelta(minutes=345)).strftime('%Y-%m-%d %H:%M:%S'))))
            elif cty.startswith('bang'):
                dates.append(str(str((row[0] + dt.timedelta(minutes=360)).strftime('%Y-%m-%d %H:%M:%S'))))
            elif cty.startswith('bhut'):
                dates.append(str(str((row[0] + dt.timedelta(minutes=360)).strftime('%Y-%m-%d %H:%M:%S'))))
            else:
                dates.append(str(dt.datetime.strftime(row[0], '%Y-%m-%d %H:%M:%S')))
            values.append(float(row[1]))

        content = {
            "dates": dates,
            "values": values,
            "rundate": recentDate,
            "riverID": comid
        }
    finally:
        conn.close()
    return JsonResponse(content)

@api_view(['GET'])
@authentication_classes((TokenAuthentication, SessionAuthentication,))
def getHistoricHIWAT(request):
    comid = request.GET.get('comid')
    cty = request.GET.get('cty')
    hdates = []
    hvalues= []

    conn = psycopg2.connect(host="192.168.10.35", database="servirFloodHiwat", user="postgres", password="changeit2")
    cur = conn.cursor()
    try:
        query = "select historydate, historyvalue from history" + cty + " where comid = " + str(comid) + " order by historydate"
        cur.execute(query)
        rows = cur.fetchall()
        for row in rows:
            mydate = str(dt.datetime.strftime(row[0], '%Y-%m-%d %H:%M:%S'))
            hdates.append(mydate)
            hvalues.append(row[1])
            # print (str(row[0]) + " : " + str(row[1]))
        # return hdates,hvalues, hdates[0], hdates[-1]
        content = {
            "mydate": mydate,
            "hdates": hdates,
            "hvalues": hvalues
        }
    finally:
        conn.close()
    return JsonResponse(content)

@api_view(['GET'])
@authentication_classes((TokenAuthentication, SessionAuthentication,))
def getreturnPeriodHIWAT(request):
    comid = request.GET.get('comid')
    cty = request.GET.get('cty')
    conn = psycopg2.connect(host="192.168.10.35", database="servirFloodHiwat", user="postgres", password="changeit2")
    cur = conn.cursor()
    content={}
    try:
        query = "SELECT max, two, ten, twenty FROM returnperiod" + cty + " where comid = " + str(comid)
        cur.execute(query)
        rows = cur.fetchall()
        return_max = rows[0][0]
        return_20 = rows[0][3]
        return_10 = rows[0][2]
        return_2 = rows[0][1]

        content = {
            "return_max" : return_max,
            "return_2" : return_2,
            "return_10" : return_10,
            "return_20" : return_20
        }
    finally:
        conn.close()
    return JsonResponse(content)
    # return return_max, return_2, return_10, return_20

@api_view(['GET'])
@authentication_classes((TokenAuthentication, SessionAuthentication,))
def getForecastHIWATCSV(request):
    comid = request.GET.get('comid')
    cty = (str(request.GET.get('cty'))).lower()
    recentDate = request.GET.get('forecastDate')
    if recentDate is None:
        recentDate = getRecentDate(comid, cty)
    print (recentDate)
    print("public.forecast" + cty + str(recentDate).replace("-", ""))
    conn = psycopg2.connect(host="192.168.10.35", database="servirFloodHiwat", user="postgres", password="changeit2")
    cur = conn.cursor()
    response = HttpResponse(content_type='text/csv')
    try:
        query = "SELECT forecastdate, forecastvalue FROM public.forecast" + cty + str(recentDate).replace("-", "") + " where comid =" \
                + str(comid) + " and runDate = '" + str(recentDate) + "' order by forecastdate"

        cur.execute(query)
        rows = cur.fetchall()
        # // CSV starts herer
        response['Content-Disposition'] = 'attachment; filename="forecastData_' + str(comid) + '.csv"'
        header = ['Dates', 'Values']
        writer = csv.writer(response)
        writer.writerow(header)

        for row in rows:
            # dates = (str(dt.datetime.strftime(row[0], '%Y-%m-%d %H:%M:%S')))
            if cty.startswith('nep'):
                dates = str(str((row[0] + dt.timedelta(minutes=345)).strftime('%Y-%m-%d %H:%M:%S')))
            elif cty.startswith('bang'):
                dates = str(str((row[0] + dt.timedelta(minutes=360)).strftime('%Y-%m-%d %H:%M:%S')))
            elif cty.startswith('bhut'):
                dates = str(str((row[0] + dt.timedelta(minutes=360)).strftime('%Y-%m-%d %H:%M:%S')))
            else:
                dates = str(dt.datetime.strftime(row[0], '%Y-%m-%d %H:%M:%S'))
            values = (float(row[1]))
            writer.writerow([dates, values])
    finally:
        conn.close()
    return response

@api_view(['GET'])
@authentication_classes((TokenAuthentication, SessionAuthentication,))
def getHistoricHIWATCSV(request):
    comid = request.GET.get('comid')
    cty = request.GET.get('cty')

    conn = psycopg2.connect(host="192.168.10.35", database="servirFloodHiwat", user="postgres", password="changeit2")
    cur = conn.cursor()
    response = HttpResponse(content_type='text/csv')

    try:
        query = "select historydate, historyvalue from history" + cty + " where comid = " + str(comid) + " order by historydate"
        cur.execute(query)
        rows = cur.fetchall()
        response['Content-Disposition'] = 'attachment; filename="historicData_' + str(comid) + '.csv"'
        header = ['Dates', 'Values']
        writer = csv.writer(response)
        writer.writerow(header)
        for row in rows:
            mydate = str(dt.datetime.strftime(row[0], '%Y-%m-%d %H:%M:%S'))
            writer.writerow([mydate, row[1]])
    finally:
        conn.close()
    return response

@api_view(['GET'])
@authentication_classes((TokenAuthentication, SessionAuthentication,))
def getreturnPeriodHIWATCSV(request):
    comid = request.GET.get('comid')
    cty = request.GET.get('cty')
    conn = psycopg2.connect(host="192.168.10.35", database="servirFloodHiwat", user="postgres", password="changeit2")
    cur = conn.cursor()
    response = HttpResponse(content_type='text/csv')
    try:
        query = "SELECT max, two, ten, twenty FROM returnperiod" + cty + " where comid = " + str(comid)
        cur.execute(query)
        rows = cur.fetchall()
        return_max = rows[0][0]
        return_20 = rows[0][3]
        return_10 = rows[0][2]
        return_2 = rows[0][1]

        response['Content-Disposition'] = 'attachment; filename="retuenPeriod_' + str(comid) + '.csv"'
        header = ['max', 'twenty', 'ten', 'two']
        writer = csv.writer(response)
        writer.writerow(header)
        writer.writerow([return_max, return_20, return_10, return_2])
    finally:
        conn.close()
    return response
    # return return_max, return_2, return_10, return_20

# @app_workspace
def getMetrologicalHIWAT(request, returnType):
    json_obj = {}
    if request.method == 'GET':
        variable = None
        geom = None
        type = None
        fName = None
        path = None
        # file1 = app_workspace.path
        # file = os.path.join(app_workspace.path, 'geojson/Basin_Balephi.geojson')

        #if request.GET.get('geom'):
        #    geom = request.GET['geom']
        if request.GET.get('geom'):
            poly_geojson = json.loads(request.GET['geom'])
            geom = shapely.geometry.shape(poly_geojson)

        if request.GET.get('type'):
            type = request.GET['type']

        if request.GET.get('variable'):
            variable = request.GET['variable']

        if request.GET.get('fName'):
            fName = request.GET['fName']
            # file = os.path.join(app_workspace.path, f'geojson/{fName}')
            file = os.path.join(staticLocation, f'geojson/{fName}')
            try:
                with open(file) as f:
                    gFile = json.load(f)
                    geom = gFile['features'][0]['geometry']
            except Exception as e:
                err = e
                # print(e)
            # t = geojson.load(fName)['features']['']

        if request.GET.get('dTime'):
            dTime = request.GET['dTime']
            path = os.path.join(HIWAT_storage, dTime)
            if os.path.exists(path + '12'):
                path = path + '12'
            elif os.path.exists(path + '18'):
                path = path + '18'
            else:
                path = 'None'
        try:
            ts = get_poylgon_values(variable,geom,type, path, returnType)
            return ts
            # json_obj["time_series"] = ts["plot"]
            # json_obj["type"] = type
            # json_obj["success"] = "success"
        except Exception as e:
            print(str(e))
            return "NULL"
            # json_obj["error"] = "Error processing request: "+str(e)

    # return JsonResponse(json_obj)

@app_workspace
def getMetrologicalHIWATCSV(request, app_workspace):
    return getMetrologicalHIWAT(request, returnType="CSV")

def getMetrologicalHIWATJSON(request):
    r=getMetrologicalHIWAT(request, returnType="JSON")
    return JsonResponse(r)

