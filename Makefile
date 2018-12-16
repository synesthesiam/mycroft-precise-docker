.PHONY: docker

docker:
	docker build . -t synesthesiam/mycroft-precise:amd64
