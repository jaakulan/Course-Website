all:
	rm -rf __pycache__
	env FLASK_APP=app.py flask run --host=localhost
