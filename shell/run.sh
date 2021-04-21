#!/bin/bash

current_time=$(date +"%d%m%y-%H%M%S")
echo "Results will be stored in $current_time"
export current_time
cd /storage/users/anderhva || exit
mkdir "$current_time"
cd "$current_time" || exit
mkdir "logs"
mkdir "results"
cd /home/anderhva/project-thesis || exit

module load Python/3.8.2-GCCcore-9.3.0
module load gurobi/9.1
cd "$GUROBI_HOME" || exit
python setup.py build -b "$HOME"/.cache/gurobipy install --user
cd /home/anderhva/project-thesis || exit

for file_path in ./input/instance/*
do
	file_name="$(basename -- "$file_path")"
	instance_name=${file_name%.*}
	export instance_name
	echo "Running $instance_name"
	python3 -m arc_flow.mathematical_model.arc_flow_model
done