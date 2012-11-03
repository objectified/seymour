class SeleniumTestResult(object):
    def __init__(self, orig_selenium_command, response, extra_info):
        self.orig_selenium_command = orig_selenium_command 
        self.response = response 
        self.extra_info = extra_info 

    def __repr__(self):
        return self.orig_selenium_command + ' ' + self.extra_info + ' ' + str(self.response)
