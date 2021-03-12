#!/bin/bash

cp -R ~/Repositories/project-thesis-lean/ ~/Repositories/project-thesis-solstorm
cd ~/Repositories/project-thesis-solstorm/ || exit
rm -rf requirements.txt
rm -rf venv
rm -rf output
rm -rf .git
rm -rf .gitignore
rm -rf .idea
find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf && find . -name ".DS_Store" -delete && find . -name "__pycache__" -delete
scp -r /Users/andersvandvik/Repositories/project-thesis-solstorm/ anderhva@solstorm-login.iot.ntnu.no:/home/anderhva
cd ~/Repositories || exit
rm -rf ~/Repositories/project-thesis-solstorm/
cd ~/Repositories/project-thesis-lean/ || exit