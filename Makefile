upload-instances:
	scp -r /Users/andersvandvik/Repositories/project-thesis-lean/input/ anderhva@solstorm-login.iot.ntnu.no:/home/anderhva/project-thesis-solstorm/input/

upload-project:
	./shell/upload_project.sh

prepare:
	. ./shell/prepare.sh

run:
	./shell/run.sh

install:
	./shell/install.sh