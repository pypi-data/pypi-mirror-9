from stimator import *
#from stimator.model import isPairOfNums
from nose.tools import *

def test_M1():
    """test Model __init__ empty ()"""
    m = Model()
    assert isinstance(m, Model)

def test_M2():
    """test Model __init__ with title"""
    m = Model("My first model")
    assert isinstance(m, Model)
    assert m.metadata['title'] == "My first model"
    assert m.name == "My first model"

def test_react1():
    """test Model.set_reaction(string, int or float)"""
    m = Model("My first model")
    m.set_reaction('v1',"A->B", 4)
    m.set_reaction('v2',"B->C", 2.0)
    assert isinstance(m.reactions.v1, model.Reaction)
    assert isinstance(m.reactions.v2, model.Reaction)
    assert m.reactions.v1.name == 'v1'
    assert m.reactions.v2.name == 'v2'
    assert m.reactions.v1()== str(float(4))+ "*A"
    assert m.reactions.v2()== str(float(2.0))+"*B"
    check, msg = m.checkRates()
    assert check 

def test_react2():
    """test Model.react(string, string)"""
    m = Model("My first model")
    m.set_reaction('v1', "A->B", " 4*A/(p1+A)-B ")
    m.setp('p1', 2)
    assert (m.reactions.v1.name) == 'v1'
    assert isinstance(m.reactions.v1, model.Reaction)
    assert m.reactions.v1()== "4*A/(p1+A)-B"
    check, msg = m.checkRates()
    assert check 

def test_react2b():
    """test Model.react(string, string) with math functions"""
    m = Model("My first model")
    m.set_reaction('v1', "A->B", " 4*sqrt(A)/(p1+sin(A))-B ")
    m.setp('p1', 2)
    assert (m.reactions.v1.name) == 'v1'
    assert isinstance(m.reactions.v1, model.Reaction)
    assert m.reactions.v1() == "4*sqrt(A)/(p1+sin(A))-B"
    check, msg = m.checkRates()
    assert check 

def test_react2c():
    """test Model.react(string, string) with kinetics functions"""
    m = Model("My first model")
    m.set_reaction('v1', "A->B", " 4*A*step(t,1.0)")
    m.setp('p1', 2)
    assert (m.reactions.v1.name) == 'v1'
    assert isinstance(m.reactions.v1, model.Reaction)
    assert m.reactions.v1() == "4*A*step(t,1.0)"
    check, msg = m.checkRates()
    assert check 

@raises(model.BadStoichError)
def test_react3():
    """test Bad stoichiometry"""
    m = Model("My first model")
    m.set_reaction('v1', "A->##B", " 4*A/(p1+A)-B ")

def test_react4():
    """test Bad rate law (unknown ID)"""
    m = Model("My first model")
    m.set_reaction('v1', "A->B", " 4*A/(p2+A)-B ")
    m.setp('p1',2)
    assert (m.reactions.v1.name) == 'v1'
    assert isinstance(m.reactions.v1, model.Reaction)
    assert m.reactions.v1() == "4*A/(p2+A)-B"
    check, msg = m.checkRates()
    assert not check 

def test_react5():
    """test Bad rate law (malformed expression)"""
    m = Model("My first model")
    m.set_reaction('v1', "A->B", " 4*A/(p1+A-B ")
    m.setp('p1',2)
    assert (m.reactions.v1.name) == 'v1'
    assert isinstance(m.reactions.v1, model.Reaction)
    assert m.reactions.v1() == "4*A/(p1+A-B"
    check, msg = m.checkRates()
    assert not check 

def test_react6():
    """test Bad rate law (fp overflow)"""
    m = Model("My first model")
    m.set_reaction('v1', "A->B", " 1e100**10000 * 4*A/(p1+A)-B ")
    m.setp('p1',2)
    assert (m.reactions.v1.name) == 'v1'
    assert isinstance(m.reactions.v1, model.Reaction)
    assert m.reactions.v1() == "1e100**10000 * 4*A/(p1+A)-B"
    check, msg = m.checkRates()
    assert not check 

def test_par1():
    """test assignment of parameters"""
    m = Model("My first model")
    m.setp('p1', 4)
    m.parameters.p2 = 3.0
    assert isinstance(m.parameters.p1, model.ConstValue)
    assert (m.parameters.p1.name) == "p1"
    assert isinstance(m.parameters.p2, model.ConstValue)
    assert (m.parameters.p2.name) == "p2"
    assert m.parameters.p1 == 4.0
    assert m.parameters.p2 == 3.0

def test_par_in_rates1():
    """test assignment of parameters 'local' to reactions"""
    m = Model("My first model")
    m.set_reaction('v1', "A->B", " p2*A/(p1+A)-B ", pars={'p1':4})
    m.setp('p2', 3.0)
    assert (m.reactions.v1.name) == 'v1'
    assert isinstance(m.reactions.v1, model.Reaction)
    assert m.reactions.v1()== "p2*A/(p1+A)-B"
    check, msg = m.checkRates()
    assert check 
    assert isinstance(m.parameters.v1.p1, model.ConstValue)
    assert (m.parameters.v1.p1.name) == "p1"
    assert isinstance(m.parameters.p2, model.ConstValue)
    assert (m.parameters.p2.name) == "p2"
    assert m.parameters.v1.p1 == 4.0
    assert m.parameters.p2 == 3.0

def test_par_from_rates1():
    """test rate expressions with parameters 'local' to reactions"""
    m = Model("My first model")
    m.set_reaction('v1', "A->B", " p2*A/(p1+A)-B ", pars={'p1':4})
    m.set_reaction('v2', "B->C", "2*v1.p1*B")
    m.setp('p2', 3.0)
    assert (m.reactions.v2.name) == 'v2'
    assert isinstance(m.reactions.v1, model.Reaction)
    assert m.reactions.v2()== "2*v1.p1*B"
    check, msg = m.checkRates()
    assert check 
    assert isinstance(m.parameters.v1.p1, model.ConstValue)
    assert (m.parameters.v1.p1.name) == "p1"
    assert isinstance(m.parameters.p2, model.ConstValue)
    assert (m.parameters.p2.name) == "p2"
    assert m.parameters.v1.p1 == 4.0
    assert m.parameters.p2 == 3.0

def test_par2():
    """test assignment of parameters with bounds"""
    m = Model("My first model")
    m.parameters.p1 = 4
    m.parameters.p2 = 3.0
    m.parameters.p1.set_bounds((1,10)) #tuple or list
    m.parameters.p2.set_bounds([1, 9.5])
    m.parameters.p3 = 5
    m.parameters.p4 = 6
    m.set_bounds('p4',(1, 8.5)) # or uncertainty function
    m.setp('p5',5)
    m.parameters.p5.bounds = model.Bounds('?',0,10)
    assert m.parameters.p1 == 4.0
    assert m.parameters.p2 == 3.0
    assert m.parameters.p3 == 5.0
    assert m.parameters.p4 == 6.0
    assert m.parameters.p3.bounds is None
    assert isinstance(m.parameters.p1.bounds, model.Bounds)
    assert m.parameters.p1.bounds.lower == 1.0
    assert m.parameters.p1.bounds.upper == 10.0
    assert isinstance(m.parameters.p2.bounds, model.Bounds)
    assert m.parameters.p2.bounds.lower == 1.0
    assert m.parameters.p2.bounds.upper == 9.5
    assert isinstance(m.parameters.p4.bounds, model.Bounds)
    assert m.parameters.p4.bounds.lower == 1.0
    assert m.parameters.p4.bounds.upper == 8.5
    assert isinstance(m.parameters.p5, model.ConstValue)
    assert (m.parameters.p5.name) == "p5"
    assert m.parameters.p5 == 5.0
    assert m.parameters.p5.bounds.lower == 0.0
    assert m.parameters.p5.bounds.upper == 10.0
    m.parameters.p4.reset_bounds()
    assert m.parameters.p4.bounds is None

def test_par_in_rates2():
    """test assignment of 'local' parameters with bounds"""
    m = Model("My first model")
    m.set_reaction('v1', "A->B", " p2*A/(p1+A)-B ", pars={'p1':4})
    m.setp('p2', 3.0)
    m.parameters.v1.p1.set_bounds((1,10)) #tuple or list
    m.parameters.p2.set_bounds([1, 9.5])
    m.parameters.p3 = 5
    assert m.parameters.v1.p1 == 4.0
    assert m.parameters.p2 == 3.0
    assert m.parameters.p3 == 5.0
    assert m.parameters.p3.bounds is None
    assert isinstance(m.parameters.v1.p1.bounds, model.Bounds)
    assert m.parameters.v1.p1.bounds.lower == 1.0
    assert m.parameters.v1.p1.bounds.upper == 10.0
    assert isinstance(m.parameters.p2.bounds, model.Bounds)
    assert m.parameters.p2.bounds.lower == 1.0
    assert m.parameters.p2.bounds.upper == 9.5

def test_transf1():
    """test transf(int or float)"""
    m = Model("My first model")
    m.set_transformation('t1',4)
    m.set_transformation('t2',2.0)
    assert isinstance(m.transformations.t1, model.Transformation)
    assert isinstance(m.transformations.t2, model.Transformation)
    assert (m.transformations.t1.name) == 't1'
    assert (m.transformations.t2.name)== 't2'
    assert m.transformations.t1() == str(float(4))
    assert m.transformations.t2() == str(float(2.0))
    check, msg = m.checkRates()
    assert check 

def test_transf2():
    """test transf(string)"""
    m = Model("My first model")
    m.set_reaction('v1', "A+B -> C", 3)
    m.set_transformation('t1', " p2*A/(p1+A)-B ", dict(p2=3))
    m.parameters.p1 = 2
    assert isinstance(m.transformations.t1, model.Transformation)
    assert (m.transformations.t1.name) == 't1'
    assert m.transformations.t1() == "p2*A/(p1+A)-B"
    check, msg = m.checkRates()
    print msg
    assert check 
    assert isinstance(m.parameters.t1.p2, model.ConstValue)
    assert (m.parameters.t1.p2.name) == "p2"
    assert m.parameters.t1.p2 == 3.0

def test_printmodel():
    """test print(model)"""
    import math
    m = Model('My first model')
    m.set_reaction('v1', "A+B -> C"  , 3)
    m.set_reaction('v2', "    -> A"  , rate = math.sqrt(4.0)/2)
    m.set_reaction('v3', "C   ->  "  , "V3 * C / (Km3 + C)")
    m.set_reaction('v4', "B   ->  "  , "2*B")
    m.set_transformation('t1', "A*4 + C")
    m.set_transformation('t2', "sqrt(2*A)")
    m.set_variable_dXdt('D',"-2 * D")
    m.parameters.B  = 2.2
    m.parameters.myconstant = 2 * m.parameters.B / 1.1 # should be 4.0
    m.parameters.V3 = 0.5
    m.parameters.V3.set_bounds([0.1, 1.0])
    m.parameters.Km3 = 4
    m.set_init(A = 1.0, C = 1, D = 1)
    m.init.C.set_bounds((1,3))
    #print should not raise an Exception
    print (m)

def test_clonemodel():
    """test model.copy()"""
    import math
    m = Model('My first model')
    m.set_reaction('v1', "A+B -> C"  , 3)
    m.set_reaction('v2', "    -> A"  , rate = math.sqrt(4.0)/2)
    m.set_reaction('v3', "C   ->  "  , "V3 * C / (Km3 + C)")
    m.set_reaction('v4', "B   ->  "  , "2*B")
    m.set_transformation('t1', "A*4 + C")
    m.set_transformation('t2', "sqrt(2*A)")
    m.set_variable_dXdt('D',"-2 * D")
    m.parameters.B  = 2.2
    m.parameters.myconstant = 2 * m.parameters.B / 1.1 # should be 4.0
    m.parameters.V3 = 0.5
    m.parameters.V3.set_bounds([0.1, 1.0])
    m.parameters.Km3 = 4
    m.set_init(A = 1.0, C = 1, D = 1)
    m.init.C.set_bounds((1,3))
    m2 = m.copy()
    assert m2 == m

def test_init1():
    """test assignment of Model.init"""
    m = Model("My first model")
    m.parameters.p1 = 4
    m.parameters.p2 = 3.0
    m.set_init(x = 1, y = 2.0)
    assert m.init.x == 1.0
    assert m.init.y == 2.0

def test_iter_reactions():
    """test iteration of reactions using reactions()"""
    import math
    m = Model('My first model')
    m.set_reaction('v1', "A+B -> C"  , 3)
    m.set_reaction('v2', "    -> A"  , rate = math.sqrt(4.0)/2)
    m.set_reaction('v3', "C   ->  "  , "V3 * C / (Km3 + C)")
    m.set_reaction('v4', "B   ->  "  , "2*B")
    m.set_transformation('t1', "A*4 + C")
    m.set_transformation('t2', "sqrt(2*A)")
    m.set_variable_dXdt('D',"-2 * D")
    assert len(m.reactions) == 5
    names = [v.name for v in m.reactions]
    rates = [v() for v in m.reactions]
    reags = [v._reagents for v in m.reactions]
    assert names[0] == 'v1'
    assert names[1] == 'v2'
    assert names[2] == 'v3'
    assert names[3] == 'v4'
    assert names[4] == 'd_D_dt'
    assert rates[0] == '3.0*A*B'
    assert rates[3] == '2*B'
    assert reags[0][0][0] == 'A'
    assert reags[0][0][1] == 1.0
    assert reags[0][1][0] == 'B'
    assert reags[0][1][1] == 1.0
    assert len(reags[1]) == 0
    assert len(reags[2]) == 1
    assert len(reags[3]) == 1

def test_iter_transf():
    """test iteration of transformations using transformations()"""
    import math
    m = Model('My first model')
    m.set_reaction('v1', "A+B -> C"  , 3)
    m.set_reaction('v2', "    -> A"  , rate = math.sqrt(4.0)/2)
    m.set_reaction('v3', "C   ->  "  , "V3 * C / (Km3 + C)")
    m.set_reaction('v4', "B   ->  "  , "2*B")
    m.set_transformation('t1', "A*4 + C")
    m.set_transformation('t2', "sqrt(2*A)")
    m.set_variable_dXdt('D',"-2 * D")
    assert len(m.transformations) == 2
    names = [v.name for v in m.transformations]
    rates = [v() for v in m.transformations]
    assert names[0] == 't1'
    assert names[1] == 't2'
    assert rates[0] == 'A*4 + C'
    assert rates[1] == 'sqrt(2*A)'

def test_iter_variables():
    """test iteration of variables using and varnames"""
    import math
    m = Model('My first model')
    m.set_reaction('v1', "A+B -> C"  , 3)
    m.set_reaction('v2', "    -> A"  , rate = math.sqrt(4.0)/2)
    m.set_reaction('v3', "C   ->  "  , "V3 * C / (Km3 + C)")
    m.set_reaction('v4', "B   ->  "  , "2*B")
    m.set_transformation('t1', "A*4 + C")
    m.set_transformation('t2', "sqrt(2*A)")
    m.set_variable_dXdt('D',"-2 * D")
    xx = m.varnames
    assert isinstance(xx, list)
    assert len(xx) == 4
    assert xx == ['A', 'B', 'C', 'D']

def test_iter_extvariables():
    """test iteration of external variables using extvariables"""
    import math
    m = Model('My first model')
    m.set_reaction('v1', "A+B -> C"  , 3)
    m.set_reaction('v2', "    -> A"  , rate = math.sqrt(4.0)/2)
    m.set_reaction('v3', "C   ->  "  , "V3 * C / (Km3 + C)")
    m.set_reaction('v4', "B   ->  "  , "2*B")
    m.set_transformation('t1', "A*4 + C")
    m.set_transformation('t2', "sqrt(2*A)")
    m.set_variable_dXdt('D',"-2 * D")
    m.parameters.B  = 2.2
    m.parameters.myconstant = 2 * m.parameters.B / 1.1 # should be 4.0
    m.parameters.V3 = 0.5
    m.parameters.V3.set_bounds([0.1, 1.0])
    m.parameters.Km3 = 4
    m.set_init(A = 1.0, C = 1, D = 1)
    m.init.C.set_bounds((1,3))
    xx = m.extvariables
    assert isinstance(xx, list)
    assert len(xx) == 1
    assert xx == ['B']

def test_iter_parameters():
    """test iteration of parameters using parameters()"""
    import math
    m = Model('My first model')
    m.set_reaction('v1', "A+B -> C"  , 3)
    m.set_reaction('v2', "    -> A"  , rate = math.sqrt(4.0)/2)
    m.set_reaction('v3', "C   ->  "  , "V3 * C / (Km3 + C)")
    m.set_reaction('v4', "B   ->  "  , "2*B")
    m.set_transformation('t1', "A*4 + C")
    m.set_transformation('t2', "sqrt(2*A)")
    m.set_variable_dXdt('D',"-2 * D")
    m.parameters.B  = 2.2
    m.parameters.myconstant = 2 * m.parameters.B / 1.1 # should be 4.0
    m.parameters.V3 = 0.5
    m.parameters.V3.set_bounds([0.1, 1.0])
    m.parameters.Km3 = 4
    m.set_init(A = 1.0, C = 1, D = 1)
    pp = m.parameters
    assert len(pp) == 4
    names = [x.name for x in m.parameters]
    assert names.sort() == ['B', 'myconstant','Km3', 'V3'].sort()
    values = [x for x in m.parameters]
    values.sort()
    should_values = [2.2, 4.0, 0.5, 4.0]
    should_values.sort()
    for v1,v2 in zip(values, should_values):
        assert_almost_equal(v1, v2)

def test_iter_uncertain():
    """test iteration of uncertain parameters using uncertain()"""
    import math
    m = Model('My first model')
    m.set_reaction('v1', "A+B -> C"  , 3)
    m.set_reaction('v2', "    -> A"  , rate = math.sqrt(4.0)/2)
    m.set_reaction('v3', "C   ->  "  , "V3 * C / (Km3 + C)")
    m.set_reaction('v4', "B   ->  "  , "2*B")
    m.set_transformation('t1', "A*4 + C")
    m.set_transformation('t2', "sqrt(2*A)")
    m.set_variable_dXdt('D',"-2 * D")
    m.setp('B', 2.2)
    m.parameters.myconstant = 2 * m.getp('B') / 1.1 # should be 4.0
    m.parameters.V3 = 0.5
    m.parameters.V3.set_bounds([0.1, 1.0])
    m.parameters.Km3 = 4
    m.parameters.Km3.set_bounds((0,5))
    m.set_init(A = 1.0, C = 1, D = 1)
    m.init.A.set_bounds((1,3))
    uu = m.with_bounds
    assert len(uu) == 3
    names = [x.name for x in m.with_bounds]
    for n in ['V3', 'Km3', 'init.A']:
        assert n in names
    should_values = {'V3':(0.1, 1.0), 'Km3':(0.0,5.0), 'init.A':(1.0,3.0)}
    for b in uu:
        assert_almost_equal(b.bounds.lower, should_values[b.name][0])
        assert_almost_equal(b.bounds.upper, should_values[b.name][1])

def test_reassignment2():
    """test reassignment of reactions"""
    m = Model("My first model")
    m.set_reaction('v1', "A -> B"  , 4)
    m.set_reaction('v2', "B -> C"  , 2.0)
    assert isinstance(m.reactions.v1, model.Reaction)
    assert isinstance(m.reactions.v2, model.Reaction)
    assert (m.reactions.v1.name) == 'v1'
    assert (m.reactions.v2.name) == 'v2'
    assert m.reactions.v1()== str(float(4))+ "*A"
    assert m.reactions.v2()== str(float(2.0))+"*B"
    check, msg = m.checkRates()
    assert check 
    m.set_reaction('v2',"D->C", 2.0)
    assert isinstance(m.reactions.v1, model.Reaction)
    assert isinstance(m.reactions.v2, model.Reaction)
    assert (m.reactions.v1.name) == 'v1'
    assert (m.reactions.v2.name) == 'v2'
    assert m.reactions.v1()== str(float(4))+ "*A"
    assert m.reactions.v2()== str(float(2.0))+"*D"
    check, msg = m.checkRates()
    assert check 

def test_reassignment3():
    """test change of variables by reassignment of reactions"""
    m = Model("My first model")
    m.set_reaction('v1', "A -> B"  , 4)
    m.set_reaction('v2', "B -> C"  , 2.0)
    assert len(m.varnames) == 3
    assert m.varnames == ['A', 'B', 'C']
    check, msg = m.checkRates()
    assert check 
    m.set_reaction('v2',"B->D", 2.0)
    xx = m.varnames
    assert len(xx) == 3
    assert xx == ['A', 'B', 'D']
    check, msg = m.checkRates()
    assert check 

## @raises(model.BadTypeComponent)
## def test_reassignment4():
##     """test illegal type reassignment (reactions)"""
##     m = Model("My first model")
##     m.set_reaction('v1', "A -> B"  , 4)
##     m.set_reaction('v2', "B -> C"  , 2.0)
##     assert len(m.varnames) == 3
##     assert m.varnames == ['A', 'B', 'C']
##     check, msg = m.checkRates()
##     assert check 
##     m.setp('v2', 3.14)
##     xx = m.varnames
##     assert len(xx) == 3
##     assert xx == ['A', 'B', 'C']
##     check, msg = m.checkRates()
##     assert check 

## @raises(model.BadTypeComponent)
## def test_reassignment5():
##     """test illegal type reassignment (parameters)"""
##     m = Model("My first model")
##     m.set_reaction('v1', "A -> B"  , 4)
##     m.set_reaction('v2', "B -> C"  , 2.0)
##     m.setp('Km', 4)
##     assert len(m.varnames) == 3
##     assert m.varnames == ['A', 'B', 'C']
##     check, msg = m.checkRates()
##     assert check 
##     m.set_reaction('Km', "A -> B"  , 4)
##     xx = m.varnames
##     assert len(xx) == 3
##     assert xx == ['A', 'B', 'C']
##     check, msg = m.checkRates()
##     assert check 

@raises(model.BadTypeComponent)
def test_illegal_type1():
    """test illegal type assignment"""
    m = Model("My first model")
    m.set_reaction('v1', "A->B", 4)
    m.set_reaction('v2', "B->C", 2.0)
    m.parameters.Km = [9,10,13,45]
    check, msg = m.checkRates()
    assert check 

def test_meta1():
    """test Model metadata"""
    m = Model("My first model")
    m.set_reaction('v1', "A->B", 4)
    m.set_reaction('v2', "B->C", 2.0)
    check, msg = m.checkRates()
    assert check 
    m.metadata['where'] = 'in model'
    m.metadata['for what'] = 'testing'
    assert m.metadata['where'] == 'in model'
    assert m.metadata['for what'] == 'testing'
    assert m.metadata['title'] == 'My first model'
    assert m.metadata.get('nonexistent', None) is None
    del m.metadata['where']
    assert m.metadata.get('where', None) is None
