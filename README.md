# Seymour
## Using Selenium for Nagios monitoring

### Introduction
Seymour is a library for end user monitoring of web applications by using actual browsers. It utilizes Selenium (the test automation framework) to create Nagios/NRPE plugins. This means that with Seymour, you can use Selenium based tests as Nagios service checks. Seymour takes in account warning/critical values, timeouts and also returns performance data for relevant steps in your Selenium test. You can handcraft Seymour based scripts using Python, as well as using the Selenium IDE formatter supplied by Seymour. This formatter lets you export Seymour based NRPE plugins directly from your browser.

### Requirements
* Python (2.7)
* [Selenium Server](http://seleniumhq.org/download/) (this requires a compatible Java Runtime Environment to be installed)
* [Selenium IDE](http://seleniumhq.org/download/) (only needed if you want to export tests to Seymour scripts directly)
* [Nagios](http://www.nagios.org) (or something that uses Nagios under the hood, like [Opsview](https://www.opsview.com))

### Quickstart
I'm assuming you're already somewhat familiar with Python and Nagios/NRPE. If you want to give Seymour a quick spin, you'll obviously need to install it. I prefer to use a virtualenv environment, I'm guessing you do too.

    $ git clone https://github.com/objectified/seymour.git seymour
    $ virtualenv seymour
    $ cd seymour && source bin/activate
    $ python setup.py install 

The next step is to download Selenium Server, and start it. This is as simple as executing the jar file:
    java -jar selenium-server-standalone-2.25.0.jar
    
By default, Selenium Server listens on port 4444. Now let's create our first Seymour based NRPE plugin.

```python
#!/usr/bin/env python

from seymour.seleniumbaserunner import SeleniumBaseRunner

class MySeymourCheck(SeleniumBaseRunner):
    def run(self):
        sel = self.selenium_proxy
        sel.open('/')
        sel.click('link=comments')
        sel.wait_for_page_to_load('5000')
        sel.is_text_present('minutes ago')

if __name__ == '__main__':
    check = MySeymourCheck()
    check.execute()
```

And that's it. Now to run this script, a number of arguments must be applied. Here's an example:

    $ python mycheck.py -H localhost -p 4444 -b firefox -t 30 -w 3 -c 5 -u http://news.ycombinator.com/ -n 'hacker news check'

If all goes well, you'll see a new browser starting up that opens http://news.ycombinator.com/ (Hacker News), clicks on a link with the name "comments" and validates whether the text "minutes ago" is present. At the end of the test run you should see the test results returned in NRPE format. Also, the exit status of the script execution is in accordance to [how NRPE plugins should behave](http://nagiosplug.sourceforge.net/developer-guidelines.html); it will return 0 on success, 1 if a warning state has been reached, 2 if a critical state has been reached, and 3 if some error occurred which is "unknown". Play around with the script to see how it will behave when you supply values that should fail. You can see a list of the arguments with their meanings by running the following command:

    $ python mycheck.py --help

Note that the timeout argument is a global timeout which is used for the entire run of the test, whereas the warning and critical thresholds apply to individual steps. 
As for the syntax in the script, you can simply use the API exposed by the Python bindings for Selenium Remote Control to invoke commands, which is documented over at [Selenium HQ](http://seleniumhq.org), except that you do not explicitly set up a connection to the Selenium Server yourself - this is handled by Seymour using the arguments given upon execution. 

You can also use Selenium IDE to generate a similar script for you. In order to make this work, you first need to install the Selenium IDE Firefox plugin. Once you have done so, you go to "Options" -> "Options..." -> "Formats" -> "Add", delete the contents of the textarea and paste the contents of the js file in the Seymour formatter/ directory into the textarea, give it the name "Seymour", and save it. Now you can export tests that you record using Selenium IDE to Seymour NRPE plugins by choosing "File" -> "Export Test Case as..". You will probably want to tweak the test case a bit before or after exporting, as tests that are recorded with Selenium IDE may not always be exactly what you want.

If you want to see exactly what is going on while you're building your test and manually executing it, you can call the set\_speed method to slow down the call sequence.

### How Seymour works
What Seymour does under the hood is proxying method calls to the Python driver for Selenium Remote Control. While proxying these calls, some method calls are interesting, in the sense that we want to do more with them than what they would usually do. Interesting methods are divided in three categories:
* Benchmarkable methods; these are methods that we want to benchmark in order to produce NRPE performance data
* Test methods; these are method that test for a condition, and should influence the exit code that is returned
* Step change methods; these methods mark the beginning of a new HTTP request

It is important to know which methods fall in which category, if you want to understand how Seymour results are being returned. Here goes:
* Benchmarkable methods: 'open', 'open\_window', 'wait\_for\_condition', 'wait\_for\_page\_to\_load', 'wait\_for\_frame\_to\_load', 'wait\_for\_popup', 'go\_back'
* Test methods: 'is\_alert\_present', 'is\_checked', 'is\_confirmation\_present', 'is\_cookie\_present', 'is\_editable', 'is\_element\_present', 'is\_ordered', 'is\_prompt\_present', 'is\_something\_selected', 'is\_text\_present', 'is\_visible'
* Step change methods: 'open', 'open\_window', 'click', 'go\_back'
Seymour intercepts calls to these methods and wraps them with appropriate code for e.g. benchmarking and storing a test result in memory for reporting back all errors. When you run a Seymour based check, you will see labels such as 'step1\_time', 'step2\_time' and so on in the performance data. This means that one of the step change methods has been invoked, so new performance data is recorded for this step. You can also set your own name when entering a new step so that your performance data makes more sense to a human, by calling set\_step\_name before calling a method that triggers a step change. Here's an example:

```python
#!/usr/bin/env python

from seymour.seleniumbaserunner import SeleniumBaseRunner

class MySeymourCheck(SeleniumBaseRunner):
    def run(self):
        sel = self.selenium_proxy
        sel.set_step_name('homepage')
        sel.open('/')
        sel.set_step_name('comments')
        sel.click('link=comments')
        sel.wait_for_page_to_load('5000')
        sel.is_text_present('minutes ago')

if __name__ == '__main__':
    check = MySeymourCheck()
    check.execute()
```

### Seymour in production
As you may have figured out by now, you will need a machine with a browser to run these tests. Your Nagios machine or Opsview masters/slaves probably don't have X installed (which is understandable), so I'd recommend having a few dedicated (virtual) machines that run one or more Selenium Server instances, so that you can point he Seymour based plugins to them through the -H/-p parameters. If you'd like to keep these machines slim, you could choose to use an in memory X server like Xvfb. In such a scenario, the Seymour Python module only needs to be installed on the machines you run your tests from, not on the machine that carries out the actual tests.

