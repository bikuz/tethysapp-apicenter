from django.http import JsonResponse, HttpResponse
import datetime as dt
import psycopg2, json,decimal, datetime, csv
# from rest_framework.authentication import SessionAuthentication
import scipy.stats as sp
import numpy as np
from datetime import timedelta
# from rest_framework import

from django.http import JsonResponse
from rest_framework.authentication import TokenAuthentication,SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes


def check_for_decimals(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError

def getRecentDate(comid, cty):
    conn = psycopg2.connect(host="192.168.10.72", database="servirFlood_ECMWF", user="postgres", password="changeit2")
    cur = conn.cursor()
    query = 'select max(rundate) as rundate from public.forecast' + cty + ' where comid = ' + comid + ' order by rundate desc'

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

@api_view(['GET'])
@authentication_classes((TokenAuthentication, SessionAuthentication,))
def getFeaturesECMWFHKH(request):
    cty =request.GET.get('cty')
    country = cty + "River"
    json_obj = {}
    conn = psycopg2.connect(host="192.168.10.72", database="servirFlood_ECMWF", user="postgres", password="changeit2")
    cur = conn.cursor()
    feature_collection={}
    try:
        query = 'select comid, risk, ST_AsGeoJSON(geom) AS geometry FROM public."' + country + '"'
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
    finally:
        conn.close()
    json_obj["feature"] = feature_collection
    return JsonResponse(feature_collection)
    # return json.dumps(feature_collection, indent=None, default=check_for_decimals)

@api_view(['GET'])
@authentication_classes((TokenAuthentication, SessionAuthentication,))
def getreturnPeriodECMWFHKH(request):
    comid = request.GET.get('comid')
    cty = request.GET.get('cty')
    conn = psycopg2.connect(host="192.168.10.72", database="servirFlood_ECMWF", user="postgres", password="changeit2")
    cur = conn.cursor()
    content={}
    try:
        query = "SELECT max, two, ten, twenty FROM public.returnreriods" + cty + " where comid = " + str(comid)
        cur.execute(query)
        rows = cur.fetchall()
        return_max = str(rows[0][0])
        return_20 = str(rows[0][3])
        return_10 = str(rows[0][2])
        return_2 = str(rows[0][1])

        content = {
            "max" : return_max,
            "two" : return_2,
            "ten" : return_10,
            "twenty" : return_20
        }
    finally:
        conn.close()
    return JsonResponse(content)
    # return return_max, return_2, return_10, return_20

@api_view(['GET'])
@authentication_classes((TokenAuthentication, SessionAuthentication,))
def getreturnPeriodECMWHKH(request):
    comid = request.GET.get('comid')
    cty = request.GET.get('cty')
    conn = psycopg2.connect(host="192.168.10.72", database="servirFlood_ECMWF", user="postgres", password="changeit2")
    cur = conn.cursor()
    content={}
    try:

        query = "SELECT max, two, ten, twenty FROM public.returnreriods" + cty + " where comid = " + str(comid)
        cur.execute(query)
        rows = cur.fetchall()
        return_max = str(rows[0][0])
        return_20 = str(rows[0][3])
        return_10 = str(rows[0][2])
        return_2 = str(rows[0][1])

        content = {
            "two" : return_2,
            "ten" : return_10,
            "twenty" : return_20
        }
    finally:
        conn.close()
    return JsonResponse(content)

@api_view(['GET'])
@authentication_classes((TokenAuthentication, SessionAuthentication,))
def getHistoricECMWFHKH(request):
    comid = request.GET.get('comid')
    cty = request.GET.get('cty')
    hdates = []
    hvalues= []

    conn = psycopg2.connect(host="192.168.10.72", database="servirFlood_ECMWF", user="postgres", password="changeit2")
    cur = conn.cursor()
    content={}
    try:
        query = "select historydate, historyvalue from public.history" + cty + " where comid = " + str(comid) + " order by historydate"
        cur.execute(query)
        rows = cur.fetchall()
        for row in rows:
            mydate = str(dt.datetime.strftime(row[0], '%Y-%m-%d %H:%M:%S'))
            hdates.append(mydate)
            hvalues.append(row[1])
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
def getFlowDurationCurveECMWFHKH(request):
    comid = request.GET.get('comid')
    cty = request.GET.get('cty')
    hdates = []
    hvalues= []
    prob=[]
    sorted_daily_avg1 =[]
    conn = psycopg2.connect(host="192.168.10.72", database="servirFlood_ECMWF", user="postgres", password="changeit2")
    cur = conn.cursor()
    try:
        query = "select historydate, historyvalue from public.history" + cty +" where comid = " + str(comid) + " order by historydate"
        cur.execute(query)
        rows = cur.fetchall()
        for row in rows:
            mydate = str(dt.datetime.strftime(row[0], '%Y-%m-%d %H:%M:%S'))
            hdates.append(mydate)
            hvalues.append(row[1])
        sorted_daily_avg = np.sort(hvalues)[::-1]
        ranks = len(sorted_daily_avg) - sp.rankdata(sorted_daily_avg, method='average')
        # calculate probability of each rank
        prob = [100 * (ranks[i] / (len(sorted_daily_avg) + 1))
                for i in range(len(sorted_daily_avg))]
        for i in range (len(sorted_daily_avg)):
            sorted_daily_avg1.append(sorted_daily_avg[i])
    finally:
        conn.close()
    content = {
        "prob": prob,
        "sorted_daily_avg1": sorted_daily_avg1
    }
    return JsonResponse(content)
    # return prob, sorted_daily_avg1


@api_view(['GET'])
@authentication_classes((TokenAuthentication,SessionAuthentication,))
def getForecastECMWFHKH(request):
    print("okokoko")
    comid = request.GET.get('comid')
    cty = request.GET.get('cty')
    runDate = request.GET.get('forecastDate')

    if runDate is None:
        # runDate = dt.datetime.now().date() - timedelta(days=0)
        runDate = getRecentDate(comid, cty)

    dates = []
    hres_dates = []
    mean_values = []
    hres_values = []
    min_values = []
    max_values = []
    std_dev_lower_values = []
    std_dev_upper_values = []
    return_obj = {}
    content={}
    # print (runDate)
    conn = psycopg2.connect(host="192.168.10.72", database="servirFlood_ECMWF", user="postgres", password="changeit2")
    cur = conn.cursor()

    try:
        query = "SELECT forecastdate, high_res, maxval, meanval, minval, std_dev_range_lower, std_dev_range_upper FROM public.forecast" + cty + " where comid =" \
                + str(comid) + " and rundate = '" + str(runDate) + "' and high_res <> 'NaN' order by forecastdate"
        print(query)
        cur.execute(query)
        rows = cur.fetchall()
        for row in rows:
            hres_dates.append(str(dt.datetime.strftime(row[0],'%Y-%m-%d %H:%M:%S')))
            # hres_values.append(row[1])

            if 'nan' not in str(row[2]):
                dates.append(str(dt.datetime.strftime(row[0],'%Y-%m-%d %H:%M:%S')))
                max_values.append(float(row[2]))
                mean_values.append(float(row[3]))
                min_values.append(float(row[4]))
                std_dev_lower_values.append(row[5])
                std_dev_upper_values.append(row[6])
                hres_values.append(row[1])
        content = {
            "hres_dates": hres_dates,
            "dates": dates,
            "max_values": max_values,
            "mean_values": mean_values,
            "min_values": min_values,
            "std_dev_lower_values": std_dev_lower_values,
            "std_dev_upper_values": std_dev_upper_values,
            "hres_values": hres_values,
            "runDate": runDate
        }
    finally:
        conn.close()
        print("connection close")
    return JsonResponse(content)

@api_view(['GET'])
@authentication_classes((TokenAuthentication, SessionAuthentication,))
def getEnsembleCSVECMWFHKH(request):
    comid = request.GET.get('comid')
    cty = request.GET.get('cty')
    runDate = request.GET.get('forecastDate')

    if runDate is None:
        runDate =  getRecentDate(comid, cty)  #dt.datetime.now().date() - timedelta(days=0)

    # conn = psycopg2.connect(host="192.168.10.35", database="servirFlood_ECMWF", user="postgres", password="changeit2")
    conn = psycopg2.connect(host="192.168.10.72", database="servirFlood_ECMWF", user="postgres", password="changeit2")
    cur = conn.cursor()
    query = "SELECT forecastdate, ensemble1, ensemble2, ensemble3, ensemble4, ensemble5, ensemble6, ensemble7, ensemble8, ensemble9, ensemble10, ensemble11, ensemble12, ensemble13, " \
            "ensemble14, ensemble15, ensemble16, ensemble17, ensemble18, ensemble19, ensemble20, ensemble21, ensemble22, ensemble23, ensemble24, ensemble25, ensemble26," \
            "ensemble27, ensemble28, ensemble29, ensemble30, ensemble31, ensemble32, ensemble33, ensemble34, ensemble35, ensemble36, ensemble37, ensemble38, ensemble39," \
            "ensemble40, ensemble41, ensemble42, ensemble43, ensemble44, ensemble45, ensemble46, ensemble47, ensemble48, ensemble49, ensemble50, ensemble51, ensemble52 " \
            "FROM public.ensemble" + str(cty) + " where comid =" \
            + str(comid) + " and rundate = '" + str(runDate) + "' order by forecastdate"

    cur.execute(query)
    rows = cur.fetchall()
    response = HttpResponse(content_type='text/csv')

    try:

        response['Content-Disposition'] = 'attachment; filename="forecastData_' + str(comid) + '.csv"'
        header = ['Dates','ensemble1','ensemble2','ensemble3','ensemble4','ensemble5','ensemble6','ensemble7','ensemble8',
                  'ensemble9','ensemble10','ensemble11','ensemble12','ensemble13','ensemble14','ensemble15','ensemble16',
                  'ensemble17','ensemble18','ensemble19','ensemble20','ensemble21','ensemble22','ensemble23','ensemble24',
                  'ensemble25','ensemble26','ensemble27','ensemble28','ensemble29','ensemble30','ensemble31','ensemble32',
                  'ensemble33','ensemble34','ensemble35','ensemble36','ensemble37','ensemble38','ensemble39','ensemble40',
                  'ensemble41','ensemble42','ensemble43','ensemble44','ensemble45','ensemble46','ensemble47','ensemble48',
                  'ensemble49','ensemble50','ensemble51','ensemble52']
        writer = csv.writer(response)
        writer.writerow(header)

        for row in rows:
            hres_dates = (str(dt.datetime.strftime(row[0],'%Y-%m-%d %H:%M:%S')))
            # dates.append(str(dt.datetime.strftime(row[0],'%Y-%m-%d %H:%M:%S')))
            ensemble1 = (float(row[1]))
            ensemble2 = (float(row[2]))
            ensemble3 = (float(row[3]))
            ensemble4 = (float(row[4]))
            ensemble5 = (float(row[5]))
            ensemble6 = (float(row[6]))
            ensemble7 = (float(row[7]))
            ensemble8 = (float(row[8]))
            ensemble9 = (float(row[9]))
            ensemble10 = (float(row[10]))
            ensemble11 = (float(row[11]))
            ensemble12 = (float(row[12]))
            ensemble13 = (float(row[13]))
            ensemble14 = (float(row[14]))
            ensemble15 = (float(row[15]))
            ensemble16 = (float(row[16]))
            ensemble17 = (float(row[17]))
            ensemble18 = (float(row[18]))
            ensemble19 = (float(row[19]))
            ensemble20 = (float(row[20]))
            ensemble21 = (float(row[21]))
            ensemble22 = (float(row[22]))
            ensemble23 = (float(row[23]))
            ensemble24 = (float(row[24]))
            ensemble25 = (float(row[25]))
            ensemble26 = (float(row[26]))
            ensemble27 = (float(row[27]))
            ensemble28 = (float(row[28]))
            ensemble29 = (float(row[29]))
            ensemble30 = (float(row[30]))
            ensemble31 = (float(row[31]))
            ensemble32 = (float(row[32]))
            ensemble33 = (float(row[33]))
            ensemble34 = (float(row[34]))
            ensemble35 = (float(row[35]))
            ensemble36 = (float(row[36]))
            ensemble37 = (float(row[37]))
            ensemble38 = (float(row[38]))
            ensemble39 = (float(row[39]))
            ensemble40 = (float(row[40]))
            ensemble41 = (float(row[41]))
            ensemble42 = (float(row[42]))
            ensemble43 = (float(row[43]))
            ensemble44 = (float(row[44]))
            ensemble45 = (float(row[45]))
            ensemble46 = (float(row[46]))
            ensemble47 = (float(row[47]))
            ensemble48 = (float(row[48]))
            ensemble49 = (float(row[49]))
            ensemble50 = (float(row[50]))
            ensemble51 = (float(row[51]))
            ensemble52 = (float(row[52]))
            writer.writerow([hres_dates,ensemble1, ensemble2, ensemble3, ensemble4, ensemble5, ensemble6, ensemble7,
                             ensemble8, ensemble9, ensemble10, ensemble11, ensemble12, ensemble13, ensemble14, ensemble15,
                             ensemble16, ensemble17, ensemble18, ensemble19, ensemble20, ensemble21, ensemble22, ensemble23,
                             ensemble24, ensemble25, ensemble26, ensemble27, ensemble28, ensemble29, ensemble30, ensemble31,
                             ensemble32, ensemble33, ensemble34, ensemble35, ensemble36, ensemble37, ensemble38, ensemble39,
                             ensemble40, ensemble41, ensemble42, ensemble43, ensemble44, ensemble45, ensemble46, ensemble47,
                             ensemble48, ensemble49, ensemble50, ensemble51, ensemble52])
    finally:
        conn.close()
    return response

@api_view(['GET'])
@authentication_classes((TokenAuthentication, SessionAuthentication,))
def getForecastCSVECMWFHKH(request):
    comid = request.GET.get('comid')
    cty = request.GET.get('cty')
    runDate = request.GET.get('forecastDate')

    if runDate is None:
        runDate =  getRecentDate(comid, cty)  #dt.datetime.now().date() - timedelta(days=0)

    conn = psycopg2.connect(host="192.168.10.72", database="servirFlood", user="postgres", password="changeit2")
    cur = conn.cursor()
    response = HttpResponse(content_type='text/csv')
    try:
        query = "SELECT forecastdate, high_res, maxval, meanval, minval, std_dev_range_lower, std_dev_range_upper FROM public.forecast" + str(cty) + "n where comid =" \
                + str(comid) + " and rundate = '" + str(runDate) + "' order by forecastdate"

        cur.execute(query)
        rows = cur.fetchall()

        response['Content-Disposition'] = 'attachment; filename="forecastData_' + str(comid) + '.csv"'
        header = ['Dates', 'hres','max','mean','min','std_dev_lower','std_dev_upper']
        writer = csv.writer(response)
        writer.writerow(header)

        for row in rows:
            hres_dates = (str(dt.datetime.strftime(row[0],'%Y-%m-%d %H:%M:%S')))
            # dates.append(str(dt.datetime.strftime(row[0],'%Y-%m-%d %H:%M:%S')))
            max_values= (float(row[2]))
            mean_values=(float(row[3]))
            min_values=(float(row[4]))
            std_dev_lower_values=(row[5])
            std_dev_upper_values=(row[6])
            hres_values=(row[1])
            writer.writerow([hres_dates,hres_values,max_values,mean_values,min_values,std_dev_lower_values,std_dev_upper_values])
    finally:
        conn.close()
    return response

@api_view(['GET'])
@authentication_classes((TokenAuthentication, SessionAuthentication,))
def getreturnPeriodCSVECMWFHKH(request):
    comid = request.GET.get('comid')
    cty = request.GET.get('cty')

    conn = psycopg2.connect(host="192.168.10.72", database="servirFlood_ECMWF", user="postgres", password="changeit2")
    cur = conn.cursor()
    response = HttpResponse(content_type='text/csv')
    try:
        query = "SELECT max, two, ten, twenty FROM public.returnreriods" + str(cty) + " where comid = " + str(comid)
        cur.execute(query)
        rows = cur.fetchall()
        return_max = rows[0][0]
        return_20 = rows[0][3]
        return_10 = rows[0][2]
        return_2 = rows[0][1]

        response['Content-Disposition'] = 'attachment; filename="retuenPeriod' + str(comid) + '.csv"'
        header = ['max', 'twenty','ten','two']
        writer = csv.writer(response)
        writer.writerow(header)
        writer.writerow([return_max, return_20, return_10, return_2])
    finally:
        conn.close()
    return response

@api_view(['GET'])
@authentication_classes((TokenAuthentication, SessionAuthentication,))
def getHistoricCSVECMWFHKH(request):
    comid = request.GET.get('comid')
    cty = request.GET.get('cty')
    hdates = []
    hvalues= []
    conn = psycopg2.connect(host="192.168.10.72", database="servirFlood", user="postgres", password="changeit2")
    cur = conn.cursor()
    response = HttpResponse(content_type='text/csv')

    try:
        query = "select historydate, historyvalue from history" + str(cty) + " where comid = " + str(comid) + " order by historydate"
        cur.execute(query)
        rows = cur.fetchall()

        response['Content-Disposition'] = 'attachment; filename="historicData_' + str(comid) + '.csv"'
        header = ['Dates', 'Values']
        writer = csv.writer(response)
        writer.writerow(header)
        for row in rows:
            mydate = str(dt.datetime.strftime(row[0], '%Y-%m-%d %H:%M:%S'))
            # hdates.append(mydate)
            # hvalues.append(row[1])
            writer.writerow([mydate, row[1]])
    finally:
        conn.close()
    return response

@api_view(['GET'])
@authentication_classes((TokenAuthentication, SessionAuthentication,))
def getFlowDurationCurveCSVECMWFHKH(request):
    comid = request.GET.get('comid')
    cty = request.GET.get('cty')
    hdates = []
    hvalues= []
    sorted_daily_avg1 =[]
    conn = psycopg2.connect(host="192.168.10.72", database="servirFlood", user="postgres", password="changeit2")
    cur = conn.cursor()
    content={}
    try:
        query = "select historydate, historyvalue from history" + str(cty) + " where comid = " + str(comid) + " order by historydate"
        cur.execute(query)
        rows = cur.fetchall()
        for row in rows:
            mydate = str(dt.datetime.strftime(row[0], '%Y-%m-%d %H:%M:%S'))
            hdates.append(mydate)
            hvalues.append(row[1])
        sorted_daily_avg = np.sort(hvalues)[::-1]
        ranks = len(sorted_daily_avg) - sp.rankdata(sorted_daily_avg, method='average')
        # calculate probability of each rank
        prob = [100 * (ranks[i] / (len(sorted_daily_avg) + 1))
                for i in range(len(sorted_daily_avg))]
        for i in range (len(sorted_daily_avg)):
            sorted_daily_avg1.append(sorted_daily_avg[i])
        content = {
            "prob": prob,
            "sorted_daily_avg1": sorted_daily_avg1
        }
    finally:
        conn.close()
    return JsonResponse(content)
    # return prob, sorted_daily_avg1