from django.http import JsonResponse, HttpResponse
import datetime as dt
import psycopg2, json,decimal, datetime, csv
from rest_framework.authentication import TokenAuthentication,SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes

import scipy.stats as sp
import numpy as np
from datetime import timedelta

def check_for_decimals(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError

@api_view(['GET'])
@authentication_classes((TokenAuthentication, SessionAuthentication,))
def getForecastCSV(request):
    comid = request.GET.get('comid')
    runDate = dt.datetime.now().date() - timedelta(days=0)
    conn = psycopg2.connect(host="192.168.10.6", database="servirFlood", user="postgres", password="changeit2")
    cur = conn.cursor()
    query = "SELECT forecastdate, high_res, maxval, meanval, minval, std_dev_range_lower, std_dev_range_upper FROM public.forecastnepal where comid =" \
            + str(comid) + " and rundate = '" + str(runDate) + "' order by forecastdate"

    cur.execute(query)
    rows = cur.fetchall()

    response = HttpResponse(content_type='text/csv')
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
    conn.close()
    return response

# @api_view(['GET'])
# @authentication_classes((TokenAuthentication, SessionAuthentication,))
# def getreturnPeriod(request):
#     comid = request.GET.get('comid')
#     cty = request.GET.get('cty')
#     conn = psycopg2.connect(host="192.168.10.6", database="servirFlood", user="postgres", password="changeit2")
#     cur = conn.cursor()
#     query = "SELECT max, two, ten, twenty FROM returnreriods" + cty + " where comid = " + str(comid)
#     cur.execute(query)
#     rows = cur.fetchall()
#
#
#     return_max = rows[0][0]
#     return_20 = rows[0][3]
#     return_10 = rows[0][2]
#     return_2 = rows[0][1]
#
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename="returnPeriod_' + str(comid) + '.csv"'
#     header = ['max', 'two', 'ten', 'twenty']
#     writer = csv.writer(response)
#     writer.writerow(header)
#
#     for row in rows:
#         # hres_dates = (str(dt.datetime.strftime(row[0], '%Y-%m-%d %H:%M:%S')))
#         # dates.append(str(dt.datetime.strftime(row[0],'%Y-%m-%d %H:%M:%S')))
#         max = (float(return_max))
#         two = (float(return_2))
#         ten = (float(return_10))
#         twenty = (float(return_20))
#         writer.writerow([max, two, ten, twenty])
#     conn.close()
#     return response
#
#     # content = {
#     #     "return_max" : return_max,
#     #     "return_2" : return_2,
#     #     "return_10" : return_10,
#     #     "return_20" : return_20
#     # }
#     # return JsonResponse(content)
#     # return return_max, return_2, return_10, return_20