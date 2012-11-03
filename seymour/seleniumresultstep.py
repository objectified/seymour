class SeleniumResultStep(object):
    def __init__(self):
        self.name = 'default'
        self.extra_info = ''
        self.benchmarked_results = []
        self.test_results = []

    def __repr__(self):
        return self.name + ' ' + self.extra_info
