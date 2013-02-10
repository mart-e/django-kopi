Kopi is a blog application using Django. This is still a work in progress.

# Installation

cp kopi/settings.py.default kopi/settings.py

Modify the following variables to match your config
  
  * ADMINS
  * DATABASES
  * TIME_ZONE
  * LANGUAGE_CODE
  * MEDIA_URL use the URL of your webserver
  * USER_THEME if you created your own theme
  * STATIC_ROOT where will be stored your static files

python manage.py collectstatic

# Dependencies

python (2.6+)
python-markdown
python-requests
django (1.4+)
django-grappelli (2.4+)
django-tagging
(all python package requires a python2 version, eg python2-markdown on archlinux)

# Theme

By default, the theme used is name "default" and defined in `theme/default/` folder.
Don't modify the content of this folder, create a new theme instead.
To create a new theme, create the following hiearchy folder

theme/
    default/ # do not change this
    mytheme/
        static/
        templates/

You can copy the files contained in the default/ folder if needed.
The file in your theme folder will overwrite the one in the default theme if present, otherwise it will use the default files.
For example, if you want to just change the default avatar image, create a new empty theme hiearchy and put you new picture in the `static/` folder.
If you want to modify only a few CSS element, don't use the full style.css file but overwrite the properties in the file custom.css in your theme folder (empty in default theme).

Finaly replace the variable `USER_THEME` in the `settings.py` file by `mytheme/`.
Collect the new static files with the command `manage.py collectstatic`.