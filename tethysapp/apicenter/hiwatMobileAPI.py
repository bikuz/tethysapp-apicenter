import datetime as dt
import psycopg2, json
from django.http import JsonResponse, HttpResponse
from http import HTTPStatus
from dateutil import tz
import pytz

from .utils import get_poylgon_values
from .config import *
from tethys_sdk.workspaces import app_workspace
import os.path

# ROUTINE FOR HIWAT MOBILE APPS ------------ Start ------>
def getHiwatWeather(request):
    gapa= request.GET.get('gapa')
    district=request.GET.get('district')
    geom=None
    cen=None
    runtype='hourly'
    path=None
    returnType='JSON'

    if request.GET.get('dTime'):
        dTime = request.GET['dTime']
        path = os.path.join(HIWAT_storage, dTime)
        if os.path.exists(path + '12'):
            path = path + '12'
        elif os.path.exists(path + '18'):
            path = path + '18'
        else:
            path = 'None'

    conn = psycopg2.connect(host="192.168.10.35", database="servirHIWAT_Extreme", user="postgres", password="changeit2")
    cur = conn.cursor()
    try:
        query = f"""SELECT id, ST_AsGeoJSON(geom) AS geometry, ST_AsGeoJSON(st_centroid(st_union(geom))) as center FROM public."gapaNapa" where "DISTRICT" = '{district}' AND "GaPa_NaPa" = '{gapa}' group by id"""
        cur.execute(query)
        rows = cur.fetchall()
        if(len(rows) > 0):
            colnames = [desc[0] for desc in cur.description]
            geomIndex = colnames.index("geometry")
            cenIndex = colnames.index("center")
            geom=json.loads(rows[0][geomIndex])
            cen=json.loads(rows[0][cenIndex])
        else:
            return HttpResponse(HTTPStatus.NOT_FOUND)

    except Exception as e:
        return HttpResponse(HTTPStatus.NOT_FOUND)
    finally:
        cur.close()
        conn.close()

    result={
        'cen':{},
        'rain':{},
        'lightning':{},
        'wind':{},
        'hail':{}
    }
    try:
        #[rain,ligntning,wind,hail]
        variable=['enspmm-prec1h','ensprob-lfa-thresh0p07','ensprob-spd10m-thresh40','ensprob-tcolg-thresh30','ensmean-tmp2m','ensmax-tmp2m','ensmin-tmp2m']
        result['cen']=cen
        result['rain'] = get_poylgon_values(variable[0],geom,runtype, path, returnType)
        result['lightning'] = get_poylgon_values(variable[1],geom,runtype, path, returnType)
        result['wind'] = get_poylgon_values(variable[2],geom,runtype, path, returnType)
        result['hail'] = get_poylgon_values(variable[3],geom,runtype, path, returnType)
        result['tmp_mean'] = get_poylgon_values(variable[4],geom,runtype, path, returnType)
        result['tmp_max'] = get_poylgon_values(variable[5],geom,runtype, path, returnType)
        result['tmp_min'] = get_poylgon_values(variable[6],geom,runtype, path, returnType)

        return JsonResponse(result)
    except Exception as e:
        print(str(e))
        return HttpResponse(HTTPStatus.NOT_FOUND)


def getHiwatStream(request):
    comid = request.GET.get('comid')
    cty = request.GET.get('cty')
    recentDate = str(request.GET.get('forecastDate'))

    if recentDate is None:
        return HttpResponse(HTTPStatus.BAD_REQUEST)
        # recentDate = getRecentDate(comid, cty)
    # print (recentDate)
    # print("public.forecast" + cty + str(recentDate).replace("-", ""))

    conn = psycopg2.connect(host="192.168.10.35", database="servirFloodHiwat", user="postgres", password="changeit2")
    cur = conn.cursor()
     
    try:
        # query="SELECT TO_CHAR(MAX(rundate), 'YYYY-MM-DD') AS max_run_date FROM public.forecast" + cty 
        # latest_runDate = cur.fetchone()[0]

        # # Compare the latest runDate with recentDate
        # if latest_runDate != recentDate:
        #     recentDate = latest_runDate
       

        # query = "SELECT forecastdate, forecastvalue FROM public.forecast" + cty  + " where comid =" \
        #         + str(comid) + " and rundate = '" + recentDate + "' order by forecastdate"

        query = "SELECT forecastdate, forecastvalue FROM public.forecast" + cty  + " where comid =" \
                + str(comid) + " order by forecastdate"
                  
        cur.execute(query)
        rows = cur.fetchall()
       
        result={
            'rundate':recentDate,
            'dates':[],
            'values':[],
            "return_max" : 0,
            "return_2" : 0,
            "return_10" : 0,
            "return_20" : 0
        }
        for row in rows:
            if cty.startswith('nep'):
                # dates = str(str((row[0] + dt.timedelta(minutes=345)).strftime('%Y-%m-%d %H:%M:%S')))
                dates = str(convertUTCDate(row[0], 'Asia/Kathmandu'))
            elif cty.startswith('bang'):
                # dates = str(str((row[0] + dt.timedelta(minutes=360)).strftime('%Y-%m-%d %H:%M:%S')))
                dates = str(convertUTCDate(row[0], 'Asia/Dhaka'))
            elif cty.startswith('bhut'):
                # dates = str(str((row[0] + dt.timedelta(minutes=360)).strftime('%Y-%m-%d %H:%M:%S')))
                dates = str(convertUTCDate(row[0], 'Asia/Thimpu'))
            else:
                dates = str(dt.datetime.strftime(row[0], '%Y-%m-%d %H:%M:%S'))

            values = (float(row[1]))
            result['dates'].append(dates)
            result['values'].append(values)

        #fetch return period values
        query = "SELECT max, two, ten, twenty FROM returnperiod" + cty + " where comid = " + str(comid)
        cur.execute(query)
        rows = cur.fetchall()

        result['return_max'] = rows[0][0]
        result['return_20'] = rows[0][3]
        result['return_10'] = rows[0][2]
        result['return_2'] = rows[0][1]
    except Exception as e:
        return HttpResponse(HTTPStatus.NOT_FOUND)
    finally:
        cur.close()
        conn.close()
    return JsonResponse(result)


def getHiwatExtreme(request):

    conn = psycopg2.connect(host="192.168.10.35", database="servirHIWAT_Extreme", user="postgres", password="changeit2")
    cur = conn.cursor()

    try:
        query = """ SELECT "DISTRICT", "GaPa_NaPa", "Rain_1", lightning_day1, moderate_hail_day1, moderate_supercell_day1, winds_40kts_day1, hraccumulated_preciptation_day1, lightning_day2, moderate_hail_day2, moderate_supercell_day2, winds_40kts_day2, hraccumulated_preciptation_day2  FROM public."gapaNapa" order by "DISTRICT", "GaPa_NaPa"; """

        cur.execute(query)
        rows = cur.fetchall()
        result={
            'DISTRICT':[],
            'GaPa_NaPa':[],
            'Rain_1':[],
            'lightning_day1':[],
            'moderate_hail_day1':[],
            'moderate_supercell_day1':[],
            'winds_40kts_day1':[],
            'hraccumulated_preciptation_day1':[],
            'lightning_day2':[],
            'moderate_hail_day2':[],
            'moderate_supercell_day2':[],
            'winds_40kts_day2':[],
            'hraccumulated_preciptation_day2':[]
            }

        for row in rows:
            result['DISTRICT'].append(row[0])
            result['GaPa_NaPa'].append(row[1])
            result['Rain_1'].append(row[2])
            result['lightning_day1'].append(row[3])
            result['moderate_hail_day1'].append(row[4])
            result['moderate_supercell_day1'].append(row[5])
            result['winds_40kts_day1'].append(row[6])
            result['hraccumulated_preciptation_day1'].append(row[7])
            result['lightning_day2'].append(row[8])
            result['moderate_hail_day2'].append(row[9])
            result['moderate_supercell_day2'].append(row[10])
            result['winds_40kts_day2'].append(row[11])
            result['hraccumulated_preciptation_day2'].append(row[12])
    except Exception as e:
        return HttpResponse(HTTPStatus.NOT_FOUND)
    finally:
        cur.close()
        conn.close()
    return JsonResponse(result)

def convertUTCDate(dateString, toTimeZone):
    fromTimeZone='UTC'
   
    
    from_zone = tz.gettz(fromTimeZone)
    to_zone = tz.gettz(toTimeZone)

    from_zone = pytz.timezone(fromTimeZone)
    to_zone = pytz.timezone(toTimeZone)    

    utc = dt.datetime.strptime(dateString,'%Y-%m-%d %H:%M:%S')

    # Tell the datetime object that it's in UTC time zone since 
    # datetime objects are 'naive' by default
    utc = utc.replace(tzinfo=from_zone)

    # Convert time zone
    return utc.astimezone(to_zone)

# <--------- End -------- ROUTINE FOR HIWAT MOBILE APPS 
