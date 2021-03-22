all:
	rm -rf __pycache__
	env FLASK_APP=Part2.py flask run --host=localhost
