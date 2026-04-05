# stock-evaluator
A service that has a main endpoint where you pass in a stock symbol. Then using  a variety of metrics evaluates it and returns a structure with different metrics and assigned values for each metric

To run locally: 
set PYTHONPATH=%CD%
python -m uvicorn app.main:app --app-dir src --host 0.0.0.0 --port 8000 --reload

To run unit test:
 - python -m pytest    &&    
 - python -m pytest --cov=src/app --cov-report=term-missing --cov-report=html --cov-branch



# Reddit setup
 1. Go to https://www.reddit.com/prefs/apps
 2. Create an App
    - Name: anything
    - Type: script
 3. Use values to set env vars, see .env.example