import pytest

@pytest.yield_fixture
def q():
    """clean and restore q's global namespace"""
    from pyq import q as _q
    cmds = 'Pc'
    vals = {}
    for c in cmds:
        vals[c] = _q('\\' + c)

    # Reset default values
    _q(r'\c 25 80')
    _q(r'\P 7')

    ns = _q.value('.')
    _q("delete from `.")

    yield _q

    _q.set('.', ns)
    for c in cmds:
        _q('\\%s %s' % (c, vals[c]))
