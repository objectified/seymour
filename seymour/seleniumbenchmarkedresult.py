from nagiosmessage import NagiosMessage 

class SeleniumBenchmarkedResult(object):
    def __init__(self, time_elapsed, orig_selenium_command, extra_info):
        self.time_elapsed = time_elapsed 
        self.unit_of_measure = NagiosMessage.UOM_SEC
        self.orig_selenium_command = orig_selenium_command 
        self.extra_info = extra_info 

    def __repr__(self):
        return self.orig_selenium_command + ' ' + self.extra_info + ' ' + str(self.time_elapsed) + self.unit_of_measure
