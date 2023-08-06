import requests
import datetime
import calendar


class DeskTime(object):
    MAIN_URL = 'https://desktime.com/api/2/json/?{params}'

    def __init__(self, app_key, username, password):
        self.api_key = self._login(app_key, username, password)
        if self.api_key is None:
            raise Exception("Authorization error")
        pass

    def _login(self, app_key, username, password):
        auth = 'appkey={appkey}&action={action}&email={email}&password={password}'
        auth = auth.format(appkey=app_key, action='authorize',
                           email=username, password=password)
        auth_url = self.MAIN_URL.format(params=auth)
        res = requests.get(auth_url)
        data = res.json()
        if not data.get(u'error', None):
            return data.get('api_key', None)
        return None

    def getAllDataForDate(self, date=datetime.datetime.now().date()):
        employees = 'apikey={apikey}&action=employees&date={date}'
        employees = employees.format(apikey=self.api_key, action='employees',
                                     date=date.isoformat())
        url = self.MAIN_URL.format(params=employees)
        res = requests.get(url)
        data = res.json()
        if not data.get('error', None):
            return data
        return None

    def getMonth(self, year, month, with_weekends=False):
        monthrange = calendar.monthrange(year, month)
        today = datetime.datetime.now().date()
        data = []
        resdata = {}
        for dayindex in range(monthrange[1]):
            day = dayindex + 1
            date = datetime.date(year, month, day)
            if date > today and date.year == today.year and today.month == date.month:
                continue
            elif date > today:
                return None
            if not with_weekends and date.weekday() in (5, 6):
                continue
            data.append(self.getAllDataForDate(date))
        for elem in data:
            resdata[elem.get('date')] = elem.get('employees')
        return data

    def getEmployee(self, employee_id):
        raise(NotImplementedError)
