run:
	NODE_ENV=development node --harmony server_node/appContainer.js

run-gunicorn:
	PYTHONPATH=./tools/perf:./server gunicorn server.appcontainer:app \
		--bind 0.0.0.0:5000 -w 4 -k gevent

# Run flask app without debug, but do serve static files
run-as-prod:
	APP_SERVE_STATIC=1 python server/app.py

serve-dev:
	gunicorn server:app --bind unix:/tmp/gunicorn_windlogger_dev.sock -w 4

poll:
	DEBUG=1 python server/poller.py

deploy:
	ansible-playbook ansible/windlogger.yml -i ansible/inventory

cli:
	PYTHONPATH=server PYTHONSTARTUP=tools/python_cli/startup.py bpython

test-fast:
	PYTHONPATH=server py.test test

clone-db:
	ansible-playbook ansible/db_backup.yml -i ansible/inventory
	scp awsnano:/tmp/db.dump .

populate-db-from-dump:
	dropdb windlogger
	createdb windlogger
	./tools/db/populate_from_dump.sh

