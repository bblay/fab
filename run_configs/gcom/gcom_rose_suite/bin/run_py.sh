. /etc/profile.d/conda.sh
conda activate sci-fab

BIN_FOLDER=$(dirname "$0")
export PYTHONPATH=$PYTHONPATH:$BIN_FOLDER

python -m $1
