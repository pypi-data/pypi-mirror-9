from expr import Expression
import pytest

class TestExpr(object):

    def test_type(self, expr):
        assert isinstance(expr, Expression)

    def test_return_val(self, expr):
        assert str(expr) == "((((a >= 10) and (a < 20)) or (b == hoge)) and (c <= 30))"

if __name__ == '__main__':
    pytest.main()
