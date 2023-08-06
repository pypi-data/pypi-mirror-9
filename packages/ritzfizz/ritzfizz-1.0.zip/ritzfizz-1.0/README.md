INSTALL YOUR THEME

These instructions assume your documentation is hosted on Github, and already working on ReadTheDocs. First let's get the proper files in place, then we will show you the proper structure.

Add requirements.txt to the project root
Open your newly created requirements.txt and add:

THEMENAME==version

For example, the RitzFizz theme would read:

ritzfizz==0.9

These package names grab the packages we have setup for you on Pypi. You can find the latest version on our front page or by searching the package in PyPi.

Modify config.py
You will need to add the following values, or modify them to match the following:

# imports go up top
import THEMENAME 

# then call the package 
html_theme = 'THEMENAME-theme'
html_theme_path = THEMENAME.get_html_theme_path()


Configure ReadTheDocs

RTD's must now be configured to use your new requirements file. It can already find configy.py, so we just need to point it to requirement.txt. In your project admin, go to Advanced Settings, click "Install your project inside a virtualenv using setup.py install". Type in "requirements.txt" in the next field. That's it! Your documents can now be rebuilt and your new theme will appear.

If you have any trouble please email us at adamw@xepler.com

