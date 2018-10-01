This is a helper utility for common usecases for the lookerapi package

Get started fast `pip install lookerapiutl`

```
import lookerapiutil as looker
apiInstance = looker.lookerapiutil(
            host='https://<<yourlooker>>.looker.com:19999/api/3.0/', 
            client_id='<<yourclientid>>', 
            client_secret = '<<yourclientsecret>>'
            )

dashboard = 2509

filterconfigs = [
    {'Brands':'Allegra K','Region':'AZ'},
    {'Brands':'Calvin Klein'},
    {'Brands':'2xist'}
    ]

apiInstance.warmdashboard(dashboard_id=dashboard, filterdicts=filterconfigs)

# optionally remove the dashboard configs:
# apiInstance.wipeDashboardSchedules(dashboard=dashboard)

```