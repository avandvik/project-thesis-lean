upload-instances:
	scp -r /Users/andersvandvik/Repositories/project-thesis/input/run/ anderhva@solstorm-login.iot.ntnu.no:/home/anderhva/project-thesis-lean/input/

upload-project:
	./shell/upload_project.sh

prepare:
	./shell/prepare.sh

run:
	./shell/run.sh $(dir_name)

install:
	./shell/install.sh