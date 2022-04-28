# myintellectualspace-back

This is the backend api for the myintellectualspace-frontend repository.

### Dependencies
- python 3.9

### How to run this application
1. Install the dependencies
2. clone this repo and `cd` into it
3. Spawn the virtual environment 
Linux: 
```
source /path-to-project/bin/activate
```
Windows
```
\path-to-project\bin\activate
```
4. With the virtual environment active, set the following environment variables
Linux:
```
export FLASK_APP=app.py
export FLASK_ENV=development
```
Windows
```
set FLASK_APP=app.py
set FLASK_ENV=development
```
5. Run the application on port 5000 with `flask run --port 5000`
