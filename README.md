# Vehicle Parking System
A platform where user can select a parking lot for parking their vehicles, as per their ease.

To create an environemnt:

1. <pre> python -m venv myenv </pre>

*(To activate)*

2. <pre> myenv/scripts/activate </pre>    
*(To activate)*

For Installation of Libraries:

<pre> pip install -r requirements.txt </pre>

Other Frontend packages:
<pre> npm install axios 
 npm install chart.js </pre> 

To run the application:

1. <pre> python -m backend.app </pre>
2. Take another terminal for frontend.

3. <pre> cd frontend </pre>
4. <pre> npm install </pre>
5. <pre> npm run dev </pre>
6. <pre> npm run serve </pre>

For backend Jobs:

1. <pre> redis-server --port 6380 </pre>

*(For beat and worker take seperate powershells and run as administrator)*


2. <pre> python -m celery -A backend.app.celery worker --loglevel=info --concurrency=1 -P solo </pre>

3. <pre> python -m celery -A backend.app.celery beat --loglevel=info</pre>

*(To check backend jobs currently, run below commands)*

4. <pre> python </pre>
   <pre>from backend.app import send_daily_reminder</pre>
    <pre> send_daily_reminder.delay()</pre>


Cloning code from GitHub:

1. <pre> restore.bat </pre> 

*(To get the packages etc.)*