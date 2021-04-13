#!/bin/bash

nj=1
text_file=$1
data_name=$(basename "${text_file}")

#./scripts/run_tts.sh ${text_file}

wav_files=espnet/egs/ljspeech/tts1/decode/${data_name}/wav_wnv/
wav_file=data/${data_name}_wavs

ls -v1 $wav_files* > ${wav_file}

./scripts/run_asr.sh ${wav_file}

cp espnet/egs/tedlium2/asr1/decode/${data_name}/${data_name}_text noisy_data/${data_name}
