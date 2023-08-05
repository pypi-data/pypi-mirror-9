import sys

import git #Requires GitPython (http://pythonhosted.org/GitPython/0.3.2)
import re
import datetime

__deultRegExp = r"\[\s*(?P<change_type>(CI|NF|BUG|INT))\s*\]\s*(\<\s*(?P<time>\d+)(?P<time_unit>(m|h))?\s*\>)?\s*(?P<task_id>\d+)\s*\:\s*(?P<description>.+)"

__reProc = re.compile(__deultRegExp)

class RepoReader:
    
    def __init__(self):
        time = None #In minutes
        changeType = None
        taskId = None
        description = None
        commitTime = None

    def __str__(self):
        return "(" + self.description + ", " + str(self.taskId) + ", " + self.changeType + "," + str(self.time) + ", " + str(self.commitTime) + ")"

def readCommits(path):
    rep = git.Repo(path)
    #head = rep.head
    #master = head.reference
    ret = []
    logs = rep.iter_commits()
    for l in logs:
        #l = c.message
        print(l.message)
        entry = RepoReader()
        try:
            res = __reProc.search(l.message)
            print(res)
            try:
                entry.changeType = res.group("change_type")
                entry.time = int(res.group("time"))
            
                if res.group("time_unit") == "h":
                    entry.time *= 60
            except:
                pass
            entry.taskId = int(res.group("task_id"))
            entry.description = res.group("description")
            
            entry.commitTime = datetime.datetime.fromtimestamp(l.committed_date)
            ret.append(entry)
            
        except:
            print(sys.exc_info()[1])
            continue

    return ret
    
        
