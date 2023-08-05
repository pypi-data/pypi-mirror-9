from redmine import Redmine
from dateutil.relativedelta import relativedelta

class RedmineWriter:

    def __init__(self, url, key=None, user=None, password=None):
        self._server = None
        self._connected = False

        if (url is None) or (key is None and (user is None or password is None)):
            self._connected = False
            return
        try:
            if key is not None:
                self._server = Redmine(url, key)
            else:
                self._server = Redmine(url,user,password)
        except:
            self._server = None
        self._connected = self._server is not None

        self.activities = None

    def isConnected(self):
        return self._connected

    def getPreviousDedicatedActivity(self,taskId):
        issue = self._server.issues[taskId]
        return iter(issue.time_entries).next().activity.id

    def getListOfActivities(self):
        return [(a.id, a.name) for a in self._server.time_entry_activities()]


    #PRE:
    #   dayofwork matches "%Y%m%d"
    #   if activity is None then is mandatory for taskId task to have at least a time assignement in the server.
    def assignDedicatedTime(self, taskId, hours, text, dayofwork, activity = None):
        if activity is None:
            activity = self.getPreviousDedicatedActivity(taskId)
        if len(text)>255:
            text = text[:256]
        dayofwork = dayofwork[:4] + "-" + dayofwork[4:6] + "-" + dayofwork[6:] + " 00:00:00"
        print(">",dayofwork)
        self._server.time_entries.new(issue_id=taskId,hours=hours,activity_id=activity,comments=text,spent_on=dayofwork)




#r = Redmine("192.168.7.101/redmine", key="95c494fc4457b0dd35273840953bfdc7c707f839")
#issueNo = 10672
#issue = r.issues[issueNo]
#aid = iter(issue.time_entries).next().activity.id
#r.time_entries.new(issue_id=10672,hours=2,activity_id=aid)
#r.time_entries.new(issue_id=10672,hours=3,activity_id=aid,comments="testing",spent_on="20131118")
