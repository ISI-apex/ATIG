# Knowledge Base APIs to store and fetch performance models

## Define the types used

```
typedef struct vertex_properties
{
	bool is_step = false, is_kernel = false, is_hardware = false;
	int id;
	Kernel_t *kernel;
	Hardware_t *hardware;
	Step_t *step;
}vertex_properties_t;

typedef struct edge_properties
{
	bool is_performance_model = false, is_kernel_map = false;
	int id;
	Performance_model_t *performance_model;
	Kernel_map_t *kernel_map;
}edge_properties_t;

typedef boost::adjacency_list<boost::vecS, boost::vecS, boost::undirectedS, vertex_properties_t, edge_properties_t> graph_t;
typedef boost::graph_traits<graph_t>::vertex_descriptor vertex_descriptor_t;
typedef graph_t::edge_descriptor edge_descriptror_t;
typedef boost::graph_traits<graph_t>::vertex_iterator vertex_iter;
typedef boost::graph_traits<graph_t>::edge_iterator edge_iter;
```

## Create a knowledge base

```
graph_t KB;
```

## Add a hardware (step, kernel) node

Define a hardware/step/kernel class

```
<Derived hardware class from Hardware_t> <hardware name>(<hardware parameter>);
<Derived kernel class from kernel_t> <kernel name>(<kernel parameter>);
<Derived step class from Step_t> <step name>(<step parameter>);
```

Manully (add a hardware node to the knowledge base) 

```
vertex_descriptor_t <name of hardware> = boost::add_vertex(KB);
KB[<name of hardware>].is_hardware = true;
KB[<name of hardware>].hardware = <reference to the hardware>;
KB[<name of hardware>].id = <id of the hardware>;
```

Through API:

```
add_hardware(graph_t &KB, Hardware_t &hardware);
add_step(graph_t &KB, Step_t &step);
add_kernel(graph_t &KB, Kernel_t &kernel);
```

## Link a hardware node with a kernel node by a performance_model edge (a step node with a kernel node)

Manully (link a hardware node with a kernel node)

```
std::pair<edge_descriptror_t, bool> <name of perofrmance model> = boost::add_edge(<name of hardware>, <name of kernel>, KB);
KB[<name of perofrmance model>].is_performance_model = ture;
KB[<name of perofrmance model>].performance_model = <reference to the performance model>;
KB[<name of perofrmance model>].id = <id of the performance model>;
```

Through API:

```
add_performance_model(graph_t &KB, Hardware_t &hardware, Kernel_t &kernel, Performance_model_t &performance_model);
add_kernel_map(graph_t &KB, Step_t &step, Kernel_t &kernel, Kernel_map_t &kernel_map);
```

## Evaluate performance based on metadata

```
performance_t <name of the result> = <name of perofrmance model>.eval(metadata_t input);
```

## Update a peroformance model

```
<name of performance model>.update(<parameters of the performance model>)
```

## Save and load the knowledge base to file

```
savegraph(graph_t &KB, std::string filename);
graph_t KB=loadgraph(std::string filename);
```

## Task Dependency Graph

Take two files as input, task_graph_edge and task_graph_node.

### task_graph_node

This file has n+1 lines for n nodes. The first line specifies the total number of nodes. In the following n lines, each line has two integers, task_id and kernel_id.

### task_graph_edge
This file has n+1 lines for n edges. The first line specifies the total number of edges. In the following n lines, each line has two task_id integers, indicating one edge in the task graph.