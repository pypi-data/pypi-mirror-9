from apycotlib import atest, writer, ERROR

class apycot_environment(object):
    def __init__(self, plan):
        self.plan = plan

    def __enter__(self):
        w  = writer.TestDataWriter(self.plan.cnxh, self.plan.plandata['eid'])
        test = atest.Test(self.plan.plandata, w)
        test.setup()
        self.test = test
        return test

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.test.global_status = ERROR
        self.test.clean()

def install_environment(test):
    texec_url = test.writer.cnxh.instance_url + str(test.texec['eid'])
    data = test.writer.cnxh.http_get(texec_url, vid='apycot.get_dependencies')
    for dep in data[0]:
        test.checkout(dep)
        test.call_preprocessor('install', dep)
