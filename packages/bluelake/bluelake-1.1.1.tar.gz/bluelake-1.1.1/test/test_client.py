# -*- coding: utf-8 -*-
import unittest

from bluelake.exc import BluelakeError
from bluelake.protocol.utils import to_bluelake_obj
from test.sample import ISampleService


class SimpleBean(object):
    pass


def create_simple_bean():
    bean = SimpleBean()
    bean.number = 1
    bean.lulu = 10000000
    bean.number2 = 1202
    bean.double1 = 1231.222
    bean.bd = "6666666666666666666666666.6666666666666"
    bean.ts = 1425624724460
    return bean


class ComplexBean(object):
    pass


def create_complex_bean():
    bean = ComplexBean()
    bean.simpleBean = create_simple_bean()
    bean.number = 32434
    return bean


class SampleTest(unittest.TestCase):

    def setUp(self):
        self.svc = ISampleService('http://localhost:8000')

    def test_basic(self):
        # count = self.svc.count('中文X')
        count = self.svc.count('1')
        count = self.svc.count('abc')
        assert count == 3

    def test_simple_obj(self):
        bean = create_simple_bean()
        result = self.svc.bean(28, 'ok', c=bean, d={'ok': bean})
        assert len(result) == 3
        assert result[0]['lulu'] == 10000000
        assert result[1] is None
        assert result[0] == result[2]

        result2 = self.svc.simpleMap(1)
        assert len(result2) == 1
        # ERROR! key is 1 rather than u'1'
        # assert isinstance(result2.get(1), dict)

    def test_complex_obj(self):
        bean = create_complex_bean()
        result = self.svc.complexBean(bean)
        assert result == to_bluelake_obj(bean.__dict__)

        result2 = self.svc.complexMap('test')
        assert isinstance(result2, dict)
        assert isinstance(result2.get('test'), list)
        assert len(result2.get('test')) == 1
        assert isinstance(result2.get('test')[0], dict)


    def test_return_none(self):
        # ERROR! All return u'' or this is ok?
        result = self.svc.returnNull()
        assert result == None
        # result2 = self.svc.returnVoid()
        # assert result2 == u''

    def test_raise_exc(self):
        try:
            self.svc.throwException('additional_infomation', '123.456')
        except Exception as e:
            pass
        except:
            assert False


def main():
    unittest.main()


if __name__ == '__main__':
    main()
