# samplEth Simulator

`samplEth` is a simulator designed to model and analyze how different sampling methods impact the query times and bandwidth requirements in the network. It allows you to tweak various parameters to simulate different conditions. 

## How to Run the Simulator

To start the simulator, run the following command in your terminal:

```bash
python3 samplEth.py
```

Once the simulation is complete, check the results folder for the output.

## Customizable Parameters

The following parameters can be adjusted to simulate different network configurations. Each section describes the purpose of the parameter and how you can modify it.

### 1. connections_per_peer

This parameter defines the range of connections each peer will have. It is set to simulate peer connections with varying numbers.

```bash
connections_per_peer = [[50, 100], [100, 150], [150, 200]]
```
This means each peer will have a random number of connections, selected from the specified ranges. You can add, remove, or modify the ranges as needed.

### 2. Custody Parameters
These parameters control the minimum custody and validator custody of peers in the network.


```bash
min_custody = 2
val_custody = 2
flat_custody = False
```

- `min_custody`: This is the baseline number of rows and columns every node is required to store, ensuring even the smallest nodes contribute to data custody.

- `val_custody`: This represents the additional rows and columns assigned per validator on a node. It is a network-wide parameter and can take fractional values, allowing nodes to increase custody incrementally based on their validator count. For example, a node with two validators would be responsible for one additional row/column if val\_custody = 0.5.
- `flat_custody`: If set to True, all peers will have uniform custody values. Set to False for varied custody values.

### 3. Poisoning Nodes
You can poison nodes based on a specific value or by percentage. This simulates potential network attacks or anomalies.

Poison by Value:
```bash
row_number = 3  # 1 -> Country, 2 -> Company, 3 -> ISP
row_value = 'prysm'
```

- `row_number`: The column you want to poison (1 for Country, 2 for Company, 3 for ISP).
- `row_value`: The value to poison in the specified column (e.g., 'prysm').

Poison by Percentage:
```bash
poison_by_percentage = True
poison_percentage = 90
```

`poison_by_percentage`: Set to True to poison a percentage of the nodes.
poison_percentage: The percentage of nodes to poison (e.g., 90%).

### 4. Query Growth Methods
Simulate different query growth patterns in the network.

Exponential Growth:
```bash
exponential_growth = False
```
When set to True, the number of queries increases exponentially in each subsequent round: 1, 2, 4, 8, 16, 32, .... 

Linear Growth:
```bash
linear_growth = True
```
The number of queries increases linearly in each round: 1, 10, 20, 30, 40, 50, ... 

Linear Constant Growth:
```bash
linear_constant_growth = False
```
Queries increase linearly up to a fixed maximum and remain constant thereafter: 1, 10, 20, 30, 40, 40, 40, ... 

Hybrid Growth:
```bash
hybrid_growth = False
```
Combines features of exponential and linear sampling: 1, 2, 4, 8, 16, 32, 64, 74, 84, 94, 104, 104, ... 

Exponential Constant Growth:
```bash
exponential_constant_growth = False
```
Similar to exponential sampling but capped at a maximum query count: 1, 2, 4, 8, 16, 32, 32, 32, ... 

Linear Growth Constant:
```bash
linear_growth_constant = 10
```
Define a constant growth rate for linear growth.

### 5. Results Folder
After running the simulation, the results will be saved in the results folder. Check this folder to analyze the output of the simulation.


## Conclusion
You can adjust these parameters to simulate various peer connection behaviors, node poisoning scenarios, and query growth patterns in a peer-to-peer network. Experimenting with these settings will help you analyze different network conditions for your research or experimentation needs.

