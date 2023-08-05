Pytest fixture "q" for pyq

Once this package is installed, you can use "q" fixture
in your pytest tests::

    def test_pyq(q):
        q.test = [1, 2, 3]
        assert q.test.count == 3


