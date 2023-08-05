from pypef import Tail


class TestTail(object):
    """Test case designed for use with py.test."""
    def assert_equal(self, result, expected):
        assert result == expected, "Incorrect result: %s, expected: %s" % (result, expected)

    def test_simple(self):
        l = range(1,100)
        t = Tail(None, 10)
        result = list(t.filter(l))
        expected = list(range(90,100))
        self.assert_equal(result, expected)

    def test_5(self):
        l = range(1,100)
        t = Tail(None, 5)
        result = list(t.filter(l))
        expected = list(range(95,100))
        self.assert_equal(result, expected)


    def test_str_5(self):
        l = range(1,100)
        t = Tail(None, "5")
        result = list(t.filter(l))
        expected = list(range(95,100))
        self.assert_equal(result, expected)

    def test_plus_5(self):
        l = range(1,100)
        t = Tail(None, "+5")
        result = list(t.filter(l))
        expected = list(range(6,100))
        self.assert_equal(result, expected)

    def test_plus_empty(self):
        l = range(1,50)
        t = Tail(None, "+50")
        result = list(t.filter(l))
        expected = []
        self.assert_equal(result, expected)