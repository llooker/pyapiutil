import lookerapi as looker
import json
import urllib
import six

if six.PY2:
    import urllib as urllib
elif six.PY3:
    import urllib.parse as urllib

class lookerapiutil:
    def __init__(self, host='',client_id='',client_secret=''):
        self.base_url = host
        self.client_id = client_id
        self.client_secret = client_secret
        self.login()

    def login(self):
        # authenticate client
        self.unauthenticated_client = looker.ApiClient(self.base_url)
        self.unauthenticated_authApi = looker.ApiAuthApi(self.unauthenticated_client)
        self.token = self.unauthenticated_authApi.login(client_id=self.client_id, client_secret=self.client_secret)
        self.client = looker.ApiClient(self.base_url, 'Authorization', 'token ' + self.token.access_token)

    def whoami(self):
        # instantiate User API client
        userApi = looker.UserApi(self.client)
        return userApi.me()

    def run_inline_query(self,format='json',query=''):
        # instantiate Look API client
        queryAPI = looker.QueryApi(self.client)
        return queryAPI.run_inline_query(format,query)

    def createDashboardSchedulePlan(self,user_id='',address='noreply@lookermail.com',cron='',dashboard_id=1,datagroup='',filters={}, name=''):
        if not user_id:
            user_id = self.whoami().id
        scheduleplan = looker.ScheduledPlanApi(self.client)
        # filters_string = '?' + urllib.parse.urlencode(filters)
        filters_string = '?' + urllib.urlencode(filters) #urlparse.urlencode(filters)
            
        config = {
                    "enabled": True,
                    "name": name,
                    "user_id": user_id,
                    "scheduled_plan_destination": [{
                        "looker_recipient": True,
                        "address": address,
                        "apply_formatting": True,
                        "apply_vis": True,
                        "format": "wysiwyg_pdf",
                        "type": "email"
                    }],
                    "title": name,
                    "filters_string": filters_string,
                    "run_as_recipient": False,
                    "send_all_results": False,
                    "timezone": "America/Los_Angeles",
                    "include_links": True
                }
        if isinstance(dashboard_id,int):
            config["dashboard_id"] = dashboard_id
        elif isinstance(dashboard_id, str):
            config["lookml_dashboard_id"] = dashboard_id

        if cron !='':
            config["crontab"] = cron
        else:
            config["datagroup"] = datagroup
        return scheduleplan.create_scheduled_plan(body=config)
    
    def wipeDashboardSchedules(self, dashboard=''):
        schedAPI = looker.ScheduledPlanApi(self.client)
        if isinstance(dashboard,int):
            dashboardSchedules =  schedAPI.scheduled_plans_for_dashboard(dashboard)
            # print(dashboardSchedules)
            for schedule in dashboardSchedules:
                # print(type(schedule.id))
                schedAPI.delete_scheduled_plan(schedule.id)
        else:
            dashboardSchedules =  schedAPI.scheduled_plans_for_lookml_dashboard(dashboard)
            for schedule in dashboardSchedules:
                schedAPI.delete_scheduled_plan(schedule.id)

    def warmdashboard(self,cron_hour=5,cron_minute=0, cron_incrementer=5,user_id='',address='noreply@lookermail.com',cron='',dashboard_id=1,datagroup='',filterdicts=[], name=''):
        if filterdicts:
            for filterdict in filterdicts:
                confirmationResponse =  self.createDashboardSchedulePlan(
                            user_id = user_id,
                            address=address,
                            cron=str(cron_minute) + ' ' + str(cron_hour) + ' * * *', #only use this OR datagroup, not both.
                            # datagroup='engagement_dag_or_looker_dag',
                            dashboard_id=dashboard_id,
                            filters= filterdict,
                            name = "(Cache Warming) {0:02}:{1:02} ".format(cron_hour,cron_minute,filterdict)
                            )
                if cron_minute + cron_incrementer >= 60:
                    cron_minute = 0
                    cron_hour += 1
                else:
                    cron_minute += cron_incrementer
            else:
                confirmationResponse =  self.createDashboardSchedulePlan(
                            user_id = user_id,
                            address=address,
                            cron=str(cron_minute) + ' ' + str(cron_hour) + ' * * *', #only use this OR datagroup, not both.
                            # datagroup='engagement_dag_or_looker_dag',
                            dashboard_id=dashboard_id,
                            filters= {},
                            name = "(Cache Warming) {0:02}:{1:02} ".format(cron_hour,cron_minute,filterdict)
                            )

