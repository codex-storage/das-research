# DAS Research

This repository hosts research on DAS for the collaboration between Codex and the EF.

The goal of the DAS Simulator is to study the problem of Data Availability Sampling, both as it is
currently proposed and with possible modifications, from the networking perspective. The simulator
is written in Python3 for accessibility, but we can imagine rewriting it at one point for
scalability and efficiency.

Currently we simulate the first part of the process which is to get segments of the 2D Reed Solomon
erasure coded block from the block builder to validators. The simulator tracks diffusion in the
network and validation progress. It is highly configurable, and it allows to explore the parameter
space in one run, generating also summary figures.

### Talks

Results from the simulator were featured in the following talks:

 * EthereumZuri.ch 2023 - Csaba Kiraly - Data Availability Sampling from the Networking Perspective,
 [see on YouTube](https://www.youtube.com/watch?v=M-xkP4FzYMQ)
 * EDCON 2023 - Leonardo Bautista-Gomez - Understanding Design Choices in Data Availability Sampling
[see on YouTube](https://www.youtube.com/watch?v=N1e_LDrKxZg)
 * EthPrague 2023 - Leonardo Bautista-Gomez - Understanding Design Choices in Data Availability Sampling
[see on YouTube](https://www.youtube.com/watch?v=Al7Jns8bCO4)
 * EthCC 2023 - Csaba Kiraly - Understanding Design Choices in Data Availability Sampling
[see on YouTube](https://www.youtube.com/watch?v=pUAVEbzLHLk)

### Versions

For recent improvements, see the [develop branch](https://github.com/codex-storage/das-research/tree/develop)

## Usage

### Prepare the environment

 * Clone the DAS repository (if not done yet) and go into the das-research directory

```
git clone https://github.com/status-im/das-research.git
cd das-research
```

 * Create a virtual environment and install the requirements

```
python3 -m venv myenv
source myenv/bin/activate
pip3 install -r DAS/requirements.txt
```

### Run the simulator

The simulation requires a configuration written in Python. To run a small example, use the `smallConf.py` configuration file:
```
python3 study.py smallConf.py
```

Results with plots will be saved in the `results` folder.

See the same example `smallConf.py` file for the description of configuration options. To derive your own simulations, copy the file, customize, and run.

## License

Licensed and distributed under either of

* MIT license: [LICENSE-MIT](LICENSE-MIT) or https://opensource.org/licenses/MIT

or

* Apache License, Version 2.0: [LICENSE-APACHEv2](LICENSE-APACHEv2) or https://www.apache.org/licenses/LICENSE-2.0

at your option. Files in this repository may not be copied, modified, or distributed except according to those terms.
