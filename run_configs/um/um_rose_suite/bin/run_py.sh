# todo: duplicated...we should use a softlink like the python file

. /etc/profile.d/conda.sh
conda activate sci-fab

BIN_FOLDER=$(dirname "$0")
export PYTHONPATH=$PYTHONPATH:$BIN_FOLDER

python -m $1
