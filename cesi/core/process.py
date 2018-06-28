from datetime import datetime, timedelta

class Process:
    """ Process Class """
    def __init__(self, dictionary):
        self.dictionary = dictionary
        self.name = self.dictionary['name']
        self.group = self.dictionary['group']
        self.start = self.dictionary['start']
        self.stop = self.dictionary['stop']
        self.now = self.dictionary['now']
        self.state = self.dictionary['state']
        self.statename = self.dictionary['statename']
        self.spawnerr = self.dictionary['spawnerr']
        self.exitstatus = self.dictionary['exitstatus']
        self.stdout_logfile = self.dictionary['stdout_logfile']
        self.stderr_logfile = self.dictionary['stderr_logfile']
        self.pid = self.dictionary['pid']

        self.start_hr = datetime.fromtimestamp(self.start).strftime('%Y-%m-%d %H:%M:%S')[11:]
        self.stop_hr = datetime.fromtimestamp(self.stop).strftime('%Y-%m-%d %H:%M:%S')[11:]
        self.now_hr = datetime.fromtimestamp(self.now).strftime('%Y-%m-%d %H:%M:%S')[11:]
        self.seconds = self.now - self.start
        self.uptime = str(timedelta(seconds=self.seconds))
        self.dictionary.update({
            'start_hr': self.start_hr,
            'stop_hr': self.stop_hr,
            'now_hr': self.now_hr,
            'uptime': self.uptime
        })

    def serialize(self):
        return self.dictionary