

class SWTestCase:
    def __init__(self):
        pass

    @classmethod
    def configure(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def run_all_test_case(self):
        for test in self.test_to_run:
            self.setUp()
            test()
            self.tearDown()

    test_to_run = []