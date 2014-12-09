# SpacePoint Fusion Mouse Controller

A simple Python command line tool to connect the [SpacePoint Fusion](http://www.pnicorp.com/markets/gaming) by PNI as a mouse controller to Windows.

## Getting Started

To run this command line tool you need to [properly install Python](http://docs.python-guide.org/en/latest/starting/install/win/) and [install virtualenv](http://virtualenv.readthedocs.org/en/latest/index.html).


1. Create a virtual environment and activate it using Powershell

 ```
 PS C:\> cd \path\to\local\repository
 PS local\repository> virtualenv venv
 PS local\repository> venv\Scripts\activate
 ```

 If using Powershell, the `activate` script is subject to the execution policies on the system. By default on Windows 7, the system’s excution policy is set to `Restricted`, meaning no scripts like the `activate` script are allowed to be executed. In order to use the script, you have to relax your system’s execution policy.

 ```PS C:\> Set-ExecutionPolicy AllSigned```
 

2. Install required packages

 ```(venv) PS local\repository> pip install -r requirements.txt```
 

3. Install the [Python for Windows extensions](http://sourceforge.net/projects/pywin32/files/)

 ```(venv) PS local\repository> easy_install path\to\exe```
 

4. Run the command line tool

 ```(venv) PS local\repository> python spacepoint.py```


5. Deactivate the virtual environment

 ```(venv) PS local\repository> deactivate```

## External Resources