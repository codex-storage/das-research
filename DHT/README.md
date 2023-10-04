# DHT simulations for DAS
Simulate the seeding and the retrieval of Ethereum DAS samples in a Kademlia-based DHT. 

## Dependencies
The DHT module relies on [`py-dht`](https://github.com/cortze/py-dht) to run, however it is already installed together with the DAS block disemination dependencies.
```shell
# once the venv is created (make sure the venv name match with the `install_dependencies.sh` one)
das-research$ bash install_dependencies.sh
```

## How to run it
To run the seeding and retrieval simulation of the DHT, these are the steps that would need to be taken:
1. configure the desired parameters in the `dhtConf.py`. NOTE: the script will create the CSV and IMG folders for you!
2. execute the experiment by running:
```shell
# venv needs to be activated
# $ source venv/bin/activate
das-research/DHT$ python3 dhtStudy.py dhtSmallConf.py 
```
the output should look like this for each of the possible configurations:
```shell
network init done in 52.08381795883179 secs
[===============================================================================================================================================================================================================================] 100%
test done in 159.97085118293762 secs
DHT fast-init jobs:8 done in 52.08381795883179 secs
12000 nodes, k=20, alpha=3, 10000 lookups
mean time per lookup  : 0.010750784277915955
mean aggr delay (secs): 0.31828715
mean contacted nodes: 8.7223
time to make 10000 lookups: 107.50784277915955 secs

done with the studies in 167.69087147712708
```
3. all the visualization graphs can be generated using the `retrieval_on_das_plotting.ipynb` notebook.
 
