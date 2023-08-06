from gq import Selector, mtable_to_dict
import pytest

class TestUtil(object):

    def test_mtable_to_dict(self, mtable, paramdict):
        assert mtable_to_dict(mtable) == paramdict

class Testgq(object):

    def test_type(self, _):
        assert isinstance(_, Selector)

    def test_params(self, _, paramdict):
        assert _.params == paramdict

    def test_val_missing(self, _):
        assert str(_._hoge) == 'hoge'
        assert str(_._fuga) == 'fuga'

if __name__ == '__main__':
    pytest.main()
