from django.http import JsonResponse, HttpResponse
import datetime as dt
import psycopg2, json,decimal, datetime, csv
from rest_framework.authentication import TokenAuthentication,SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes
import scipy.stats as sp
import numpy as np
from datetime import timedelta
# from rest_framework import

def check_for_decimals(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError

def getConnection():
    return psycopg2.connect(host="192.168.10.35", database="servirFlood_ECMWF_HKH", user="icimod", password="changeit2")

def getRecentDate(comid, cty):
    conn = getConnection() #psycopg2.connect(host="192.168.10.35", database="servirFlood_ECMWF_HKH", user="icimod", password="changeit2")
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
def getFeaturesECMWF(request):
    cty =request.GET.get('cty')
    country = cty + "River"
    json_obj = {}
    conn = getConnection() # psycopg2.connect(host="192.168.10.35", database="servirFlood_ECMWF_HKH", user="icimod", password="changeit2")
    cur = conn.cursor()
    feature_collection={}
    try:
        query = 'select comid, risk, ST_AsGeoJSON(geom) AS geometry FROM ' + country
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
def getreturnPeriodECMWF(request):
    comid = request.GET.get('comid')
    cty = request.GET.get('cty')
    conn = getConnection() # psycopg2.connect(host="192.168.10.35", database="servirFlood_ECMWF_HKH", user="icimod", password="changeit2")
    cur = conn.cursor()
    content={}
    try:
        query = "SELECT hundred, two, ten, twentyfive, five, fifty FROM public.returnperiods" + cty + " where comid = " + str(comid)
        cur.execute(query)
        rows = cur.fetchall()
        return_max = str(rows[0][0])
        return_20 = str(rows[0][3])
        return_10 = str(rows[0][2])
        return_2 = str(rows[0][1])
        return_5 = str(rows[0][4])
        return_50 = str(rows[0][5])

        content = {
            "max": return_max,
            "two": return_2,
            "ten": return_10,
            "twenty": return_20,
            "five": return_5,
            "fifty": return_50
        }
    finally:
        conn.close()
    return JsonResponse(content)
    # return return_max, return_2, return_10, return_20

@api_view(['GET'])
@authentication_classes((TokenAuthentication, SessionAuthentication,))
def getreturnPeriodECMW(request):
    comid = request.GET.get('comid')
    cty = request.GET.get('cty')
    conn = getConnection() # psycopg2.connect(host="192.168.10.35", database="servirFlood_ECMWF_HKH", user="icimod", password="changeit2")
    cur = conn.cursor()
    content={}
    try:
        query = "SELECT hundred, two, ten, twentyfive FROM public.returnperiods" + cty + " where comid = " + str(comid)
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
def getHistoricECMWF(request):
    comid = request.GET.get('comid')
    cty = request.GET.get('cty')
    hdates = []
    hvalues= []

    conn = getConnection() # psycopg2.connect(host="192.168.10.35", database="servirFlood_ECMWF_HKH", user="icimod", password="changeit2")
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
def getFlowDurationCurveECMWF(request):
    comid = request.GET.get('comid')
    cty = request.GET.get('cty')
    hdates = []
    hvalues= []
    sorted_daily_avg1 =[]
    conn = getConnection() #psycopg2.connect(host="192.168.10.35", database="servirFlood_ECMWF_HKH", user="icimod", password="changeit2")
    cur = conn.cursor()
    content={}
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
        content = {
            "prob": prob,
            "sorted_daily_avg1": sorted_daily_avg1
        }
    finally:
        conn.close()
    return JsonResponse(content)
    # return prob, sorted_daily_avg1

@api_view(['GET'])
@authentication_classes((TokenAuthentication, SessionAuthentication,))
def getForecastECMWF(request):
    comid = request.GET.get('comid')
    cty = request.GET.get('cty')
    runDate = request.GET.get('forecastDate')

    if runDate is None:
        # runDate = dt.datetime.now().date() - timedelta(days=0)
        runDate = getRecentDate(comid, cty)
        runDate = str(runDate).replace("-", "")
        query = "SELECT forecastdate, high_res, maxval, meanval, minval, std_dev_range_lower, std_dev_range_upper FROM public.forecast" + cty + " where comid =" + str(
            comid) + " and high_res <> 'NaN' order by forecastdate"
    else:
        cty = 'hkh'
        runDate = str(runDate).replace("-","")
        query = "SELECT forecastdate, high_res, maxval, meanval, minval, std_dev_range_lower, std_dev_range_upper FROM public.forecast" + cty + "_" + str(runDate) + " where comid =" \
                + str(comid) + " and high_res <> 'NaN' order by forecastdate"

    dates = []
    hres_dates = []
    mean_values = []
    hres_values = []
    min_values = []
    max_values = []
    std_dev_lower_values = []
    std_dev_upper_values = []
    return_obj = {}
    # print (runDate)
    conn = getConnection() #psycopg2.connect(host="192.168.10.35", database="servirFlood_ECMWF_HKH", user="icimod", password="changeit2")
    cur = conn.cursor()
    content={}
    try:
        # query = "SELECT forecastdate, high_res, maxval, meanval, minval, std_dev_range_lower, std_dev_range_upper FROM public.forecast" + cty + " where comid =" \
        #         + str(comid) + " and rundate = '" + str(runDate) + "' and high_res <> 'NaN' order by forecastdate"
        print(query)
        cur.execute(query)
        rows = cur.fetchall()
        
        for row in rows:
            hres_dates.append(str(dt.datetime.strftime(row[0],'%Y-%m-%d %H:%M:%S')))
            # hres_values.append(row[1])

            if  row[2]!=None:
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
    return JsonResponse(content)

def converNonetoNan(val):
    if val!=None:
        return (float(val))
    else:
        return (float('nan'))

@api_view(['GET'])
@authentication_classes((TokenAuthentication, SessionAuthentication,))
def getEnsembleCSVECMWF(request):
    comid = request.GET.get('comid')
    cty = request.GET.get('cty')
    runDate = request.GET.get('forecastDate')

    if runDate is None:
        runDate =  getRecentDate(comid, cty)  #dt.datetime.now().date() - timedelta(days=0)

    conn = getConnection() #psycopg2.connect(host="192.168.10.35", database="servirFlood_ECMWF_HKH", user="icimod", password="changeit2")
    # conn = psycopg2.connect(host="192.168.11.7", database="servirFlood_ECMWF", user="postgres", password="changeit2")
    # conn = psycopg2.connect(host="192.168.0.43", database="servirFlood_ECMWF", user="postgres", password="changeit2")
    cur = conn.cursor()
    response = HttpResponse(content_type='text/csv')

    try:
        query = "SELECT forecastdate, ensemble1, ensemble2, ensemble3, ensemble4, ensemble5, ensemble6, ensemble7, ensemble8, ensemble9, ensemble10, ensemble11, ensemble12, ensemble13, " \
                "ensemble14, ensemble15, ensemble16, ensemble17, ensemble18, ensemble19, ensemble20, ensemble21, ensemble22, ensemble23, ensemble24, ensemble25, ensemble26," \
                "ensemble27, ensemble28, ensemble29, ensemble30, ensemble31, ensemble32, ensemble33, ensemble34, ensemble35, ensemble36, ensemble37, ensemble38, ensemble39," \
                "ensemble40, ensemble41, ensemble42, ensemble43, ensemble44, ensemble45, ensemble46, ensemble47, ensemble48, ensemble49, ensemble50, ensemble51, ensemble52 " \
                "FROM public.ensemble" + str(cty) + " where comid =" \
                + str(comid) + " and rundate = '" + str(runDate) + "' order by forecastdate"

        cur.execute(query)
        rows = cur.fetchall()

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
            ensemble1 = converNonetoNan(row[1])
            ensemble2 = converNonetoNan(row[2])
            ensemble3 = converNonetoNan(row[3])
            ensemble4 = converNonetoNan(row[4])
            ensemble5 = converNonetoNan(row[5])
            ensemble6 = converNonetoNan(row[6])
            ensemble7 = converNonetoNan(row[7])
            ensemble8 = converNonetoNan(row[8])
            ensemble9 = converNonetoNan(row[9])
            ensemble10 = converNonetoNan(row[10])
            ensemble11 = converNonetoNan(row[11])
            ensemble12 = converNonetoNan(row[12])
            ensemble13 = converNonetoNan(row[13])
            ensemble14 = converNonetoNan(row[14])
            ensemble15 = converNonetoNan(row[15])
            ensemble16 = converNonetoNan(row[16])
            ensemble17 = converNonetoNan(row[17])
            ensemble18 = converNonetoNan(row[18])
            ensemble19 = converNonetoNan(row[19])
            ensemble20 = converNonetoNan(row[20])
            ensemble21 = converNonetoNan(row[21])
            ensemble22 = converNonetoNan(row[22])
            ensemble23 = converNonetoNan(row[23])
            ensemble24 = converNonetoNan(row[24])
            ensemble25 = converNonetoNan(row[25])
            ensemble26 = converNonetoNan(row[26])
            ensemble27 = converNonetoNan(row[27])
            ensemble28 = converNonetoNan(row[28])
            ensemble29 = converNonetoNan(row[29])
            ensemble30 = converNonetoNan(row[30])
            ensemble31 = converNonetoNan(row[31])
            ensemble32 = converNonetoNan(row[32])
            ensemble33 = converNonetoNan(row[33])
            ensemble34 = converNonetoNan(row[34])
            ensemble35 = converNonetoNan(row[35])
            ensemble36 = converNonetoNan(row[36])
            ensemble37 = converNonetoNan(row[37])
            ensemble38 = converNonetoNan(row[38])
            ensemble39 = converNonetoNan(row[39])
            ensemble40 = converNonetoNan(row[40])
            ensemble41 = converNonetoNan(row[41])
            ensemble42 = converNonetoNan(row[42])
            ensemble43 = converNonetoNan(row[43])
            ensemble44 = converNonetoNan(row[44])
            ensemble45 = converNonetoNan(row[45])
            ensemble46 = converNonetoNan(row[46])
            ensemble47 = converNonetoNan(row[47])
            ensemble48 = converNonetoNan(row[48])
            ensemble49 = converNonetoNan(row[49])
            ensemble50 = converNonetoNan(row[50])
            ensemble51 = converNonetoNan(row[51])
            ensemble52 = converNonetoNan(row[52])
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
def getForecastCSVECMWF(request):
    comid = request.GET.get('comid')
    cty = request.GET.get('cty')
    runDate = request.GET.get('forecastDate')

    if runDate is None:
        runDate =  getRecentDate(comid, cty)  #dt.datetime.now().date() - timedelta(days=0)

    conn = getConnection() #psycopg2.connect(host="192.168.10.35", database="servirFlood_ECMWF_HKH", user="icimod", password="changeit2")
    cur = conn.cursor()
    response = HttpResponse(content_type='text/csv')
    try:
        query = "SELECT forecastdate, high_res, maxval, meanval, minval, std_dev_range_lower, std_dev_range_upper FROM public.forecast" + str(cty) + " where comid =" \
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
def getreturnPeriodCSVECMWF(request):
    comid = request.GET.get('comid')
    cty = request.GET.get('cty')

    conn = getConnection() #psycopg2.connect(host="192.168.10.35", database="servirFlood_ECMWF_HKH", user="icimod", password="changeit2")
    cur = conn.cursor()
    response = HttpResponse(content_type='text/csv')

    try:
        query = "SELECT hundred, two, ten, twentyfive FROM public.returnperiods" + str(cty) + " where comid = " + str(comid)
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
def getHistoricCSVECMWF(request):
    comid = request.GET.get('comid')
    cty = request.GET.get('cty')
    hdates = []
    hvalues= []
    conn = getConnection() #psycopg2.connect(host="192.168.10.35", database="servirFlood_ECMWF_HKH", user="icimod", password="changeit2")
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
def getFlowDurationCurveCSVECMWF(request):
    comid = request.GET.get('comid')
    cty = request.GET.get('cty')
    hdates = []
    hvalues= []
    sorted_daily_avg1 =[]
    conn = getConnection() #psycopg2.connect(host="192.168.10.35", database="servirFlood_ECMWF_HKH", user="icimod", password="changeit2")
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
    # return prob, sorted_daily_avg
