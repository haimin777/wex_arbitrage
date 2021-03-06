import math, re, ccxt, time
from pprint import pformat



def get_data_for_graph(price1="last", price2="last"):
    print('data for: ', price1, price2)
    wex = ccxt.wex()
    data_for_graph = {}
    data = wex.fetch_tickers()
    for key in data:
        data_for_graph.update({key: data[key][price1]})
    ticker_list = list(data_for_graph.keys())
    ticker_list2 = []
    for key in ticker_list:
        ticker_list2.append("{1}/{0}".format(*key.split('/')))  # обратные тикеры

    for key in range(0, len(ticker_list)):
        # обратные котировки
        data_for_graph.update({ticker_list2[key]: 1 / (data[ticker_list[key]][price2])})

    #print(pformat(data_for_graph))
    return data_for_graph




def create_graph(data_for_graph):
    graph = {}
    jsrates = data_for_graph

    pattern = re.compile("([A-Z]{3,5})/([A-Z]{3,5})")

    try:
        for key in jsrates:
            matches = pattern.match(key)

            conversion_rate = math.log(float(jsrates[key]))
            # conversion_rate = jsrates[key]

            from_rate = matches.group(1).encode('ascii', 'ignore')

            to_rate = matches.group(2).encode('ascii', 'ignore')

            if from_rate != to_rate:
                if from_rate not in graph:
                    graph[from_rate] = {}
                graph[from_rate][to_rate] = float(conversion_rate)

    except AttributeError:
        print('Strange rate')
        pass

    # print(pformat(graph))
    # воплощение алгоритма отсюда
    #  https://gist.github.com/joninvski/701720
    return graph


# Step 1: For each node prepare the destination and predecessor
def initialize(graph, source):
    d = {}  # Stands for destination
    p = {}  # Stands for predecessor
    for node in graph:
        d[node] = float('Inf')  # We start admiting that the rest of nodes are very very far
        p[node] = None
    d[source] = 0  # For the source we know how to reach
    return d, p


def relax(node, neighbour, graph, d, p):
    # If the distance between the node and the neighbour is lower than the one I have now
    if d[neighbour] > d[node] + graph[node][neighbour]:
        # Record this lower distance
        d[neighbour] = d[node] + graph[node][neighbour]
        p[neighbour] = node


def retrace_negative_loop(p, start):
    arbitrageLoop = [start]
    next_node = start

    while True:

        next_node = p[next_node]
        if next_node not in arbitrageLoop:
            arbitrageLoop.append(next_node)
        else:
            arbitrageLoop.append(next_node)
            arbitrageLoop = arbitrageLoop[arbitrageLoop.index(next_node):]
            return arbitrageLoop


def bellman_ford(graph, source):
    d, p = initialize(graph, source)
    for i in range(len(graph) - 1):  # Run this until is converges

        for u in graph:
            for v in graph[u]:  # For each neighbour of u
                relax(u, v, graph, d, p)  # Lets relax it

    # Step 3: check for negative-weight cycles
    for u in graph:
        print('u: ', u)
        for v in graph[u]:
            #print('v: ', v)
            if d[v] < d[u] + graph[u][v]:
                return (retrace_negative_loop(p, source))
    return None


paths = []

data_for_graph = get_data_for_graph(price1='bid', price2='ask')

graph = create_graph(data_for_graph)
time.sleep(1)
for key in graph:

    path = bellman_ford(graph, key)
    if path not in paths and not None:
        paths.append(path)

for path in paths:
    if path == None:
        print("No opportunity here :(")
    else:
        print('cycle lenght:', len(path))
        money = 100
        print("Starting with %(money)i in %(currency)s" % {"money": money, "currency": path[0]})

        for i, value in enumerate(path):
            if i + 1 < len(path):
                start = path[i]
                end = path[i + 1]
                rate = math.exp(graph[start][end])
                money *= rate
                # money *= rate*0.998
                print("%(start)s to %(end)s at %(rate)f = %(money)f" % {"start": start, "end": end, "rate": rate,
                                                                        "money": money})
print("\n")
