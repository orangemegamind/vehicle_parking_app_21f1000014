echo Rebuilding project environment...

echo Creating backend\instance folder...
mkdir backend\instance

echo Setting up Python virtual environment...
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt

echo Installing frontend node modules...
cd frontend
npm install
cd ..

echo Restore complete!
pause
