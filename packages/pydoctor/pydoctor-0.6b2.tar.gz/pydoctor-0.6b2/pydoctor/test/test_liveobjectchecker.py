from pydoctor.test.test_packages import processPackage
from pydoctor.liveobjectchecker import liveCheck

def DONT_test_simple():
    system = processPackage('liveobject')
    liveCheck(system)
    mod = system.allobjects['liveobject.mod']
    assert mod.contents['m'].docstring == 'this is a docstring'
    assert 'D' in mod.contents
    D = mod.contents['D']
    B = mod.contents['B']
    assert D.name == 'D'
    assert D.baseobjects == [B]
    assert B.subclasses == [D]

    # we shouldn't find a "new" method called _C__m
    assert len(mod.contents['C'].contents) == 2
