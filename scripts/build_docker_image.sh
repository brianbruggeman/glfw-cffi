#!/usr/bin/env bash
project_folder=$(git rev-parse --show-toplevel)
repo_name=$(basename `git rev-parse --show-toplevel`)
project_name=$(python -c "print('${repo_name}'.replace('-', '_'))")
if [ -e $(command -v docker-machine) ] ; then
    echo -n "Setting up docker..." ;
    docker_env=$({docker-machine env default} 2>&1 );
    if [[ $docker_env == *"Error"* ]] ; then
        set -e
        echo
        docker-machine restart
        docker-machine env -u
        docker-machine env default
        eval $(docker-machine env default)
        set +e
    fi
    echo "done"
fi;
cd $project_folder
cmd="docker build -f ${project_folder}/Dockerfile -t $project_name ."
echo $cmd
exec $cmd
