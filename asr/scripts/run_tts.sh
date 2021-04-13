#!/bin/bash


is_root=false

if [ $# != 1 ]; then
    echo "Wrong #arguments ($#, expected 1)"
    echo "Usage: apps/run_tts.sh [options] <text file>"
    exit 1
fi

TTS_FILE=$1

#cd ..

from_tag=cpu-u18
EXTRAS=true

if [ ${is_root} = false ]; then
    # Build a container with the user account
    container_tag="${from_tag}-user-${HOME##*/}"
    docker_image=$( docker images -q espnet/espnet:${container_tag} )
    if ! [[ -n ${docker_image}  ]]; then
        echo "Building docker image..."
        build_args="--build-arg FROM_TAG=${from_tag}"
        build_args="${build_args} --build-arg THIS_USER=${HOME##*/}"
        build_args="${build_args} --build-arg THIS_UID=${UID}"
        build_args="${build_args} --build-arg EXTRA_LIBS=${EXTRAS}"

        echo "Now running docker build ${build_args} -f docker/prebuilt/Dockerfile -t espnet/espnet:${container_tag} ."
        (docker build ${build_args} -f docker/prebuilt/Dockerfile -t  espnet/espnet:${container_tag} .) || exit 1
    fi
else
    container_tag=${from_tag}
fi

#cd ..
vols="-v ${PWD}/espnet/egs:/espnet/egs
      -v ${PWD}/espnet/espnet:/espnet/espnet
      -v ${PWD}/espnet/test:/espnet/test
      -v ${PWD}/espnet/utils:/espnet/utils
      -v ${PWD}/data:/noiseqa/data
      -v ${PWD}/noisy_data:/noiseqa/noisy_data"


echo "$vols"
data_name=$(basename "${TTS_FILE}")

docker run --rm ${vols} espnet/espnet:${container_tag} bash -c "echo $PWD
                                cd /espnet/egs/ljspeech/tts1;
                                mkdir -p data;
                                cat /noiseqa/${TTS_FILE} | tr '[:lower:]' '[:upper:]' > data/${data_name};
                                /espnet/utils/synth_wav.sh data/${data_name}"

