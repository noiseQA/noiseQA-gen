 #!/bin/bash

SRC_PATH=./data/example.txt
OUTDIR=./noisy_data/example.txt

 # Can use only 1 gpu because we are not passing batches
CUDA_VISIBLE_DEVICES=2,3 python backtranslation.py --src_lang en --tgt_lang de --data_src $SRC_PATH --data_tgt $OUTDIR

