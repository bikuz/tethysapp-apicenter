from tethys_sdk.base import TethysAppBase


class App(TethysAppBase):
    """
    Tethys app class for Apicenter.
    """
    name = 'Apicenter'
    description = ''
    package = 'apicenter'  # WARNING: Do not change this value
    index = 'home'
    icon = f'{package}/images/icon.gif'
    root_url = 'apicenter'
    color = '#045c34'
    tags = ''
    enable_feedback = False
    feedback_emails = []


    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)
        url_maps = (
            UrlMap(
                name='ECMWFAPIService',
                url='apicenter/ECMWFAPIService',
                controller='apicenter.controllers.ECMWFAPIService'
            ),
            UrlMap(
                name='Purpose',
                url='apicenter/purpose',
                controller='apicenter.controllers.purpose'
            ),
            UrlMap(
                name='Registration',
                url='apicenter/registration',
                controller='apicenter.controllers.Registration'
            ),
            UrlMap(
                name='HIWATAPIService',
                url='apicenter/HIWATAPIService',
                controller='apicenter.controllers.HIWATAPIService'
            ),
            UrlMap(
                name='ECMWF_API_service_Get_Forecast_Data',
                url='apicenter/ECMWFAPIserviceGetForecastData',
                controller='apicenter.controllers.ECMWF_API_service_Get_Forecast_Data'
            ),
            UrlMap(
                name='ECMWF_API_service_Get_Historic_Data',
                url='apicenter/ECMWFAPIserviceGetHistoricData',
                controller='apicenter.controllers.ECMWF_API_service_Get_Historic_Data'
            ),
            UrlMap(
                name='HIWATAPIService_Get_Historic_Data',
                url='apicenter/HIWATAPIServiceGetHistoricData',
                controller='apicenter.controllers.HIWATAPIService_Get_Historic_Data'
            ),
            UrlMap(
                name='HIWATAPIService_Get_Return_periods',
                url='apicenter/HIWATAPIServiceGetReturnperiods',
                controller='apicenter.controllers.HIWATAPIService_Get_Return_periods'
            ),
            UrlMap(
                name='HIWATAPIService_Get_Forecast_data',
                url='apicenter/HIWATAPIServiceGetForecastdata',
                controller='apicenter.controllers.HIWATAPIService_Get_Forecast_data'
            ),
            UrlMap(
                name='HIWATAPIService_Get_ID_of_Stream',
                url='apicenter/HIWATAPIServiceGetIDofStream',
                controller='apicenter.controllers.HIWATAPIService_Get_ID_of_Stream'
            ),
            UrlMap(
                name='LoginView',
                url='apicenter/LoginView',
                controller='apicenter.controllers.LoginView'
            ),UrlMap(
                name='GetToken',
                url='apicenter/GetToken',
                controller='apicenter.controllers.GetToken'
            ),
            # # Real API code is below
            UrlMap(
                name='home',
                url='apicenter',
                controller='apicenter.controllers.home'),
            # UrlMap(
            #     name='getFeatures',
            #     url='apicenter/api/getFeatures',
            #     controller='apicenter.api.getFeatures'),
            # UrlMap(
            #     name='getFeaturesECMWF',
            #     url='apicenter/api/getFeaturesECMWF',
            #     controller='apicenter.api.getFeaturesECMWF'),
            # UrlMap(
            #     name='getFeaturesECMWFHKH',
            #     url='apicenter/HKHapi/getFeaturesECMWFHKH',
            #     controller='apicenter.HKHapi.getFeaturesECMWFHKH'),
            # UrlMap(
            #     name='getreturnPeriod',
            #     url='apicenter/api/getreturnPeriod',
            #     controller='apicenter.api.getreturnPeriod'),
            UrlMap(
                name='getreturnPeriodECMWF',
                url='apicenter/ECMWFapi/getreturnPeriodECMWF',
                controller='apicenter.ECMWFapi.getreturnPeriodECMWF'),
            # UrlMap(
            #     name='getreturnPeriodECMWFHKH',
            #     url='apicenter/HKHapi/getreturnPeriodECMWFHKH',
            #     controller='apicenter.HKHapi.getreturnPeriodECMWFHKH'),
            UrlMap(
                name='getreturnPeriodECMW',
                url='apicenter/ECMWFapi/getreturnPeriodECMW',
                controller='apicenter.ECMWFapi.getreturnPeriodECMW'),
            # UrlMap(
            #     name='getreturnPeriodECMWHKH',
            #     url='apicenter/HKHapi/getreturnPeriodECMWHKH',
            #     controller='apicenter.HKHapi.getreturnPeriodECMWHKH'),
            # UrlMap(
            #     name='getHistoric',
            #     url='apicenter/api/getHistoric',
            #     controller='apicenter.api.getHistoric'),
            UrlMap(
                name='getHistoricECMWF',
                url='apicenter/ECMWFapi/getHistoricECMWF',
                controller='apicenter.ECMWFapi.getHistoricECMWF'),
            # UrlMap(
            #     name='getHistoricECMWFHKH',
            #     url='apicenter/HKHapi/getHistoricECMWFHKH',
            #     controller='apicenter.HKHapi.getHistoricECMWFHKH'),
            # UrlMap(
            #     name='getFlowDurationCurve',
            #     url='apicenter/api/getFlowDurationCurve',
            #     controller='apicenter.api.getFlowDurationCurve'),
            UrlMap(
                name='getFlowDurationCurveECMWF',
                url='apicenter/ECMWFapi/getFlowDurationCurveECMWF',
                controller='apicenter.ECMWFapi.getFlowDurationCurveECMWF'),
            # UrlMap(
            #     name='getFlowDurationCurveECMWFHKH',
            #     url='apicenter/HKHapi/getFlowDurationCurveECMWFHKH',
            #     controller='apicenter.HKHapi.getFlowDurationCurveECMWFHKH'),
            # UrlMap(
            #     name='getForecast',
            #     url='apicenter/api/getForecast',
            #     controller='apicenter.api.getForecast'),
            UrlMap(
                name='getForecastECMWF',
                url='apicenter/ECMWFapi/getForecastECMWF',
                controller='apicenter.ECMWFapi.getForecastECMWF'),
            UrlMap(
                name='getForecastCSVECMWF',
                url='apicenter/ECMWFapi/getForecastCSVECMWF',
                controller='apicenter.ECMWFapi.getForecastCSVECMWF'),
            # UrlMap(
            #     name='getForecastECMWFHKH',
            #     url='apicenter/HKHapi/getForecastECMWFHKH',
            #     controller='apicenter.HKHapi.getForecastECMWFHKH'),
            UrlMap(
                name='getFeaturesHIWAT',
                url='apicenter/hiwatAPI/getFeaturesHIWAT',
                controller='apicenter.hiwatAPI.getFeaturesHIWAT'),
            UrlMap(
                name='getFeaturesHIWATPA',
                url='apicenter/hiwatAPI/getFeaturesHIWATPA',
                controller='apicenter.hiwatAPI.getFeaturesHIWATPA'),
            UrlMap(
                name='getForecastHIWAT',
                url='apicenter/hiwatAPI/getForecastHIWAT',
                controller='apicenter.hiwatAPI.getForecastHIWAT'),
            UrlMap(
                name='getHistoricHIWAT',
                url='apicenter/hiwatAPI/getHistoricHIWAT',
                controller='apicenter.hiwatAPI.getHistoricHIWAT'),
            UrlMap(
                name='getreturnPeriodHIWAT',
                url='apicenter/hiwatAPI/getreturnPeriodHIWAT',
                controller='apicenter.hiwatAPI.getreturnPeriodHIWAT'),

            # UrlMap(
            #     name='getreturnPeriodCSV',
            #     url='apicenter/api/getreturnPeriodCSV',
            #     controller='apicenter.api.getreturnPeriodCSV'),
            UrlMap(
                name='getreturnPeriodCSVECMWF',
                url='apicenter/ECMWFapi/getreturnPeriodCSVECMWF',
                controller='apicenter.ECMWFapi.getreturnPeriodCSVECMWF'),
            # UrlMap(
            #     name='getreturnPeriodCSVECMWFHKH',
            #     url='apicenter/HKHapi/getreturnPeriodCSVECMWFHKH',
            #     controller='apicenter.HKHapi.getreturnPeriodCSVECMWFHKH'),
            # UrlMap(
            #     name='getHistoricCSV',
            #     url='apicenter/api/getHistoricCSV',
            #     controller='apicenter.api.getHistoricCSV'),
            # UrlMap(
            #     name='getFlowDurationCurveCSV',
            #     url='apicenter/api/getFlowDurationCurveCSV',
            #     controller='apicenter.api.getFlowDurationCurveCSV'),
            # UrlMap(
            #     name='getForecastCSV',
            #     url='apicenter/api/getForecastCSV',
            #     controller='apicenter.api.getForecastCSV'),
            # UrlMap(
            #     name='getEnsembleCSV',
            #     url='apicenter/api/getEnsembleCSV',
            #     controller='apicenter.api.getEnsembleCSV'),
            UrlMap(
                name='getEnsembleCSVECMWF',
                url='apicenter/ECMWFapi/getEnsembleCSVECMWF',
                controller='apicenter.ECMWFapi.getEnsembleCSVECMWF'),
            # UrlMap(
            #     name='getEnsembleCSVECMWFHKH',
            #     url='apicenter/HKHapi/getEnsembleCSVECMWFHKH',
            #     controller='apicenter.HKHapi.getEnsembleCSVECMWFHKH'),
            UrlMap(
                name='getForecastHIWATCSV',
                url='apicenter/hiwatAPI/getForecastHIWATCSV',
                controller='apicenter.hiwatAPI.getForecastHIWATCSV'),
            UrlMap(
                name='getHistoricHIWATCSV',
                url='apicenter/hiwatAPI/getHistoricHIWATCSV',
                controller='apicenter.hiwatAPI.getHistoricHIWATCSV'),
            UrlMap(
                name='getreturnPeriodHIWATCSV',
                url='apicenter/hiwatAPI/getreturnPeriodHIWATCSV',
                controller='apicenter.hiwatAPI.getreturnPeriodHIWATCSV'),
            UrlMap(
                name='getMetrologicalHIWATCSV',
                url='apicenter/hiwatAPI/getMetrologicalHIWATCSV',
                controller='apicenter.hiwatAPI.getMetrologicalHIWATCSV'),
            UrlMap(
                name='getMetrologicalHIWATJSON',
                url='apicenter/hiwatAPI/getMetrologicalHIWATJSON',
                controller='apicenter.hiwatAPI.getMetrologicalHIWATJSON'),
            UrlMap(
                name='getHiwatWeather',
                url='apicenter/hiwatAPI/getHiwatWeather',
                controller='apicenter.hiwatAPI.getHiwatWeather'
            ),    
            UrlMap(
                name='getHiwatStreamNepal',
                url='apicenter/hiwatAPI/getHiwatStreamNepal',
                controller='apicenter.hiwatAPI.getHiwatStreamNepal'
            )
        )

        return url_maps
