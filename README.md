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

## Prepare the environment

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

## Run the simulator

```
python3 study.py smallConf.py
```

## License

Licensed and distributed under either of

* MIT license: [LICENSE-MIT](LICENSE-MIT) or https://opensource.org/licenses/MIT

or

* Apache License, Version 2.0: [LICENSE-APACHEv2](LICENSE-APACHEv2) or https://www.apache.org/licenses/LICENSE-2.0

at your option. Files in this repository may not be copied, modified, or distributed except according to those terms.
