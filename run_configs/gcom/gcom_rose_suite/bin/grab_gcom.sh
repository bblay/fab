. /etc/profile.d/conda.sh
conda activate sci-fab

echo "script dir"
BIN_FOLDER=$(dirname "$0")
export PYTHONPATH=$PYTHONPATH:$BIN_FOLDER

python -m grab_gcom
#grab_gcom.py
