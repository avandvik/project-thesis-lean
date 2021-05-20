#!/bin/bash

ssh -i ~/.ssh/id_rsa anderhva@solstorm-login.iot.ntnu.no "rm -rf /home/anderhva/project-thesis/input; exit;"
scp -prq /Users/andersvandvik/Repositories/project-thesis-lean/input/. anderhva@solstorm-login.iot.ntnu.no:/home/anderhva/project-thesis/input/