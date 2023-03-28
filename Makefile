start_benchmark:
	docker-compose up

start_local_benchmark:
	docker-compose -f docker-compose-clichouse.yml up \
    --abort-on-container-exit \
    --exit-code-from benchmark