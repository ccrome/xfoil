all:
	@echo make docker   : makes the docker image, named 'xfoil'
	@echo make run      : runs said docker.  Access the server at http://localhost:8050

docker:
	docker build -t xfoil .
run:
	docker run --rm -it -p8050:8050 xfoil

