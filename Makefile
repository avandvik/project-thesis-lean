upload-instances:
	scp -r /Users/andersvandvik/Repositories/project-thesis/input/run/ anderhva@solstorm-login.iot.ntnu.no:/home/anderhva/project-thesis-lean/input/

upload-project:
	cp -R ~/Repositories/project-thesis-lean/ ~/Repositories/project-thesis-solstorm
	rm -rf requirements.txt
	rm -rf venv
	# scp -r /Users/andersvandvik/Repositories/project-thesis-lean/ anderhva@solstorm-login.iot.ntnu.no:/home/anderhva

prepare:
	./shell/prepare.sh

run:
	./shell/run.sh $(dir_name)