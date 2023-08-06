from dispel4py.examples.graph_testing.testing_PEs import NumberProducer
from dispel4py.new.aggregate import parallelSum, parallelCount, parallelMin, parallelMax, parallelAvg

from dispel4py.new import simple_process
from dispel4py.workflow_graph import WorkflowGraph

from nose import tools

def graph_sum():
    prod = NumberProducer(1000)
    prod.name = 'NumberProducer'
    s = parallelSum()
    graph = WorkflowGraph()
    graph.connect(prod, 'output', s, 'input')
    return graph


def graph_avg():
    prod = NumberProducer(1000)
    a = parallelAvg()
    graph = WorkflowGraph()
    graph.connect(prod, 'output', a, 'input')
    return graph


def graph_min_max():
    prod = NumberProducer(1000)
    mi = parallelMin()
    ma = parallelMax()
    graph = WorkflowGraph()
    graph.connect(prod, 'output', mi, 'input')
    graph.connect(prod, 'output', ma, 'input')
    return graph


def graph_count():
    prod = NumberProducer(1000)
    c = parallelCount()
    graph = WorkflowGraph()
    graph.connect(prod, 'output', c, 'input')
    return graph


def testSum():
    sum_wf = graph_sum()
    sum_wf.flatten()
    results = simple_process.process_and_return(sum_wf, inputs={ 'NumberProducer' : [ {} ] } )
    # there should be only one result
    tools.eq_(1, len(results))
    for key in results:
        tools.eq_({ 'output' :[[499500]]} , results[key])


def testAvg():
    avg_wf = graph_avg()
    avg_wf.flatten()
    results = simple_process.process_and_return(avg_wf, inputs={ 'NumberProducer' : [ {} ] } )
    tools.eq_(1, len(results))
    for key in results:
        tools.eq_({ 'output' :[[499.5, 1000, 499500]]} , results[key])


def testCount():
    count_wf = graph_count()
    count_wf.flatten()
    results = simple_process.process_and_return(count_wf, inputs={ 'NumberProducer' : [ {} ] } )
    print results
    tools.eq_(1, len(results))
    for key in results:
        tools.eq_({ 'output' :[[1000]]} , results[key])


def testMinMax():
    min_max_wf = graph_min_max()
    min_max_wf.flatten()
    results = simple_process.process_and_return(min_max_wf, inputs={ 'NumberProducer' : [ {} ] } )
    print results
    tools.eq_(2, len(results))
    for key in results:
        if key.startswith('MinPE'):
            tools.eq_({ 'output' :[[0]]} , results[key])
        else:
            tools.eq_({ 'output' :[[999]]} , results[key])


sum_wf = graph_sum()
avg_wf = graph_avg()
min_wf = graph_min_max()
count_wf = graph_count()