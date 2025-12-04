# stock-evaluator
A service that has a main endpoint where you pass in a stock symbol. Then using  a variety of metrics evaluates it and returns a structure with different metrics and assigned values for each metric

To run locally: 
python -m uvicorn app.main:app --app-dir src --host 0.0.0.0 --port 8000 --reload

To run unit test:
python -m pytest