VENV="./myenv"

echo "Installing dependencies for DAS..."

# activate the venv or raise error if error
source $VENV/bin/activate
if [ $? -eq 0 ]; then
  echo "venv successfully sourced"
else
  echo "unable to source venv at $VENV , does it exist?"
  exit 1
fi

# make sure that the submodule module is correctly downloaded
git submodule update --init

# install requirements for DAS and py-dht and install the dht module from py-dht
pip3 install -r DAS/requirements.txt
pip3 install -r py-dht/requirements.txt
pip3 install -e py-dht
