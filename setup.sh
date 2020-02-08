
export CONDA_DIR=/cvmfs/des.opensciencegrid.org/fnal/anaconda2

source $CONDA_DIR/etc/profile.d/conda.sh

conda activate des18a

jupyter notebook --no-browser --port=8889

