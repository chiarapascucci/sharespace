<h1>SHARESPACE</h1>
<p>The files contained in this submission make up the codebase of a web-based application developed as part of the final project for my MSc in Software Development at the University of Glasgow</p>

<p>ThiS README will outline the steps needed to replicate and run the application on a local machine</p>
<hr>
<h3>Local enviroment set up</h3>
<p>This submission includes a requirements.txt file, which contains the list of packages installed in the environment that was used to developed this application</p>
<p>To successfully run the application please ensure that all packages in this file are installed using the version specified</p>
<hr>
<h3>Setting up Sharespace</h3>
<p>Having set up the environment as per the requirements.txt file, follow the steps below to run the application on your machine</p>

- navigate to the project directory in your command line (sharespace_project)
- run: python manage.py makemigrations sharespace
- run: python manage.py migrate
- these commands create the database for the application (SQLite3 file)
- To populate the database run: python populate.py (remaining in the project folder)
- to run the server and use the application in your browser run: python manage.py runserver

<p>Ensure you complete all the steps above in the given order if you wish to run the application</p>
<hr>
<h3>Folder and File Structure Overview</h3>

<h5>sharespace_project</h5>
<p>the sharespace_project directory contains some files required for Django to work</p>
<br>
<h5>templates</h5>
<p>the templates directory contains all of the html files (templates) used for this project. The sub-director registration contains the Django registration's own templates</p>
<br>
<h5>static</h5>
<p>The static folder contains static files which are needed for the functionality of the application and/or to render the application correctly</p>
<br>
<h5>population scripts</h5>
<p>within the project directory two population scripts are provided (populate.py and populate_categories.py). The populate the database with sample data (note: only populate.py should be invoked when following the steps in the previous section)</p>
<br>
<h5>media</h5>
<p>the media folder has been created to store user-uploaded data. Apart from a default image file all sub-folder inside it should be empty when first running the application</p>
<br>
<h5>sharespace</h5>
<p>the sharespace directory contains all the python files that manage the logic and data flow in the application as well as a testing module for the application, which is briefly described below</p>
<hr>
<h3>Testing</h3>
<p>this submission includes a testing module which contains the files used to run automated testing on the application using Selenium and pytest (please note that those packages are included in the requirements list)</p>
<p>to run the automated tests, please ensure:</p>

- you have Chrome, and/or Firefox, and/or Microsoft Edge installed as your browser
- navigate to the testing module in your command line
- run: pytest "name_of_the_desired_test_file". For example, to test the application in Chrome run: pytest run_tests_chrome.py

!! **note on testing with Microsoft Edge**: to achieve testing with microsofot edge a local instance of the ME driver had to be downloaded and installed. As such the path to this file was hardcoded in the test_driver_utils.py file. If you want to run tests with ME, please download the relevant driver and replace the hardcoded path with your path to this driver