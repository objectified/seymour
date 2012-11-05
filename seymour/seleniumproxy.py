import time
from collections import OrderedDict
from selenium import selenium
# from selenium.webdriver.emulation.selenium1 import DrivenSelenium

from seleniumresultstep import SeleniumResultStep
from seleniumbenchmarkedresult import SeleniumBenchmarkedResult
from seleniumtestresult import SeleniumTestResult

class SeleniumProxy(selenium, object):
    """ 
    Proxy between Nagios plugin and the Selenium RC Python driver.

    This class acts as a proxy to the Selenium RC Python driver. It intercepts
    method calls to the driver that are relevant for creating output for Nagios. It 
    categorizes calls to the driver in three segments:
    1. benchmarkable commands. These are commands sent to Selenium RC that must be 
    wrapped with benchmarking code to be able to report how long such a call has taken.
    2. test commands. These are commands sent to Selenium RC that perform tests. These 
    commands need to be wrapped with error handling code to output Nagios compatible 
    errors.
    3. step change trigger commands. These are commands sent to Selenium RC that logically
    equal a 'step' in a test run. A step equals the initiation of a new HTTP request (e.g.
    requesting a new page)
    """
    def __init__(self, host, port, browserStartCommand, browserURL):
        self.benchmarkable_commands = [
            'open', 'open_window', 'wait_for_condition', 
            'wait_for_page_to_load', 'wait_for_frame_to_load', 'wait_for_popup', 'go_back'
        ]
        self.test_commands = [
            'is_alert_present', 'is_checked', 
            'is_confirmation_present', 'is_cookie_present', 'is_editable',
            'is_element_present', 'is_ordered', 'is_prompt_present',
            'is_something_selected', 'is_text_present', 'is_visible'
        ]
        self.step_change_trigger_commands = [
            'open', 'open_window', 'click', 
            'go_back'
        ]
            
        self.steps = OrderedDict() 
        self.step_counter = 0
        self.step_prefix = 'step'
        self.active_step_name = None 
        self.custom_step_name = None

        super(SeleniumProxy, self).__init__(host,  port, browserStartCommand, browserURL)

    def set_step_name(self, name):
        self.custom_step_name = name

    def __getattribute__(self, name):
        attr = super(SeleniumProxy, self).__getattribute__(name)
        if callable(attr):
            if name in self.benchmarkable_commands:
                def benchmarkable_wrapper(*args, **kwargs):
                    if name in self.step_change_trigger_commands:
                        self.raise_step(','.join(args) + ','.join(kwargs))

                    time1 = time.time()

                    # call wrapped method
                    retval = attr(*args, **kwargs) 

                    elapsed = time.time() - time1

                    result = SeleniumBenchmarkedResult(
                        time_elapsed=elapsed, 
                        orig_selenium_command=name, 
                        extra_info=','.join(["%s" % el for el in args]) + ','.join(["%s" % el for el in kwargs])
                    )

                    self.steps[self.active_step_name].benchmarked_results.append(result)

                    return retval
                    
                return benchmarkable_wrapper
            elif name in self.test_commands:
                def test_wrapper(*args, **kwargs):
                    if name in self.step_change_trigger_commands:
                        self.raise_step(','.join(args) + ','.join(kwargs))

                    retval = attr(*args, **kwargs)

                    result = SeleniumTestResult(
                        orig_selenium_command=name, 
                        response=retval, 
                        extra_info=','.join(["%s" % el for el in args]) + ','.join(["%s" % el for el in kwargs])
                    )

                    self.steps[self.active_step_name].test_results.append(result)

                    return retval
                return test_wrapper
            else: 
                def catchall_wrapper(*args, **kwargs):
                    if name in self.step_change_trigger_commands:
                        self.raise_step(','.join(args) + ','.join(kwargs))

                    retval = attr(*args, **kwargs)

                    return retval
                return catchall_wrapper
        else:
            return attr

    def raise_step(self, step_info):
        self.step_counter += 1        

        if not self.custom_step_name:
            self.active_step_name = self.step_prefix + str(self.step_counter)
        else:
            self.active_step_name = self.custom_step_name
            self.custom_step_name = None

        step = SeleniumResultStep()
        step.name = self.active_step_name
        step.extra_info = step_info
        self.steps[self.active_step_name] = step

    def wait_for_element_present(self, locator, timeout):
        self.wait_for_condition("selenium.isElementPresent(\"%s\");" % locator.replace("\"", "\\\""), timeout)
