import sys
import signal
#import abc
import argparse
from seleniumproxy import SeleniumProxy
from nagiosmessage import NagiosMessage
from timeoutexception import TimeoutException

class SeleniumBaseRunner(object):
#    __metaclass__ = abc.ABCMeta
    selenium_proxy = None 
    proxy_running = False
    name = ''
    warning_threshold = 10
    critical_threshold = 20
    global_timeout = 50

    def __init__(self):
        parser = argparse.ArgumentParser(add_help=True)
        parser.add_argument('-H', '--host', help='selenium rc host to connect to', required=True)
        parser.add_argument('-p', '--port', help='remote selenium rc port to connect to', default=4444, type=int)
        parser.add_argument('-b', '--browser', help='browser to use on the remote control server', required=True)
        parser.add_argument('-t', '--timeout', help='timeout in seconds to use for the whole test execution', default=30, type=int)
        parser.add_argument('-w', '--warning', help='threshold to use for warning state (seconds)', default=10, type=int)
        parser.add_argument('-c', '--critical', help='threshold to use for critical state (seconds)', default=20, type=int)
        parser.add_argument('-u', '--base-url', help='base url for the test run', required=True)
        parser.add_argument('-n', '--name', help='name for the test run', required=True)
        args = parser.parse_args() 

        self.warning_threshold = args.warning
        self.critical_threshold = args.critical
        self.name = args.name
        self.global_timeout = args.timeout

        try:
            self.selenium_proxy = SeleniumProxy(args.host, args.port, args.browser, args.base_url)
            self.selenium_proxy.start()
            self.proxy_running = True
        except Exception, ex:
            'An error occurred initializing Selenium RC connection', ex

    def build_nagios_message(self):
        nagios_message = NagiosMessage()
        for step_key in sorted(self.selenium_proxy.steps.iterkeys()):
            step = self.selenium_proxy.steps[step_key] 

            # handle test results
            for test_result in step.test_results:
                if test_result.response == False:
                    nagios_message.add_msg('Test failed in ' + str(step) + ': ' + str(test_result)) 
                    nagios_message.raise_status(NagiosMessage.NAGIOS_STATUS_CRITICAL)

            # handle benchmarked results
            for benchmarked_result in step.benchmarked_results:
                nagios_message.add_perfdata(
                    label=step.name + '_time', 
                    uom=NagiosMessage.UOM_SEC, 
                    real=benchmarked_result.time_elapsed, 
                    warn=self.warning_threshold, 
                    crit=self.critical_threshold, 
                    minval='', maxval=''
                )

                if benchmarked_result.time_elapsed > self.critical_threshold:
                    nagios_message.add_msg('Critical threshold exceeded in ' + str(step) + ': ' + str(benchmarked_result))
                    nagios_message.raise_status(NagiosMessage.NAGIOS_STATUS_CRITICAL)
                elif benchmarked_result.time_elapsed > self.warning_threshold:
                    nagios_message.add_msg('Warning threshold exceeded in ' + str(step) + ': ' + str(benchmarked_result))
                    nagios_message.raise_status(NagiosMessage.NAGIOS_STATUS_WARNING)
                       
        if nagios_message.status_code == NagiosMessage.NAGIOS_STATUS_OK:
            nagios_message.add_msg('Test ' + self.name + ' succeeded')

        return nagios_message

#    @abc.abstractmethod 
    def run(self):
        return 

    def execute(self):
        def timeout_handler(signum, frame):
            raise TimeoutException()

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(self.global_timeout)

        exit_code = NagiosMessage.NAGIOS_STATUS_OK 
        try:
            self.run() 
            msg = self.build_nagios_message()
            print msg
            exit_code = msg.status_code
        except TimeoutException, tex:
            print "Test execution took too long, global timeout of", self.global_timeout, "seconds exceeded"
            exit_code = NagiosMessage.NAGIOS_STATUS_CRITICAL
        except Exception, ex:
            print "Error occurred:", ex
            exit_code = NagiosMessage.NAGIOS_STATUS_UNKNOWN
        finally:
            if(self.proxy_running == True):
                self.selenium_proxy.stop()
                self.proxy_running = False

            sys.exit(exit_code)

    def fail(self):
        pass

    def assertEqual(self):
        pass

    def assertNotEqual(self):
        pass

if __name__ == '__main__':
    runner = SeleniumBaseRunner()
    runner.execute()
