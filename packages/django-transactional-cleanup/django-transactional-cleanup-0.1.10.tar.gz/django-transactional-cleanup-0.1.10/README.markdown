# django-transactional-cleanup

django-transactional-cleanup automatically deletes old file for FileField,
ImageField and subclasses, and it also deletes files on models instance
deletion.

**Warning**: It depends on django-transaction-hooks app and you need to
configure your database backend to use a django-transactional-hooks backend or
any that use the django-transactional-hooks backend mixin. See the
documentation here: https://django-transaction-hooks.readthedocs.org/ .

## How does it work?

django-transactional-cleanup connects pre_save and post_delete signals to
special functions(these functions delete old files) for each model which app is
listed in INSTALLED_APPS above than 'django_transactional_cleanup'.

## Installation
    
    pip install django-transactional-cleanup


## Configuration

Add django_transactional_cleanup to settings.py

    INSTALLED_APPS = (
        ...
        'django_transactional_cleanup', # should go after your apps
    )

**django_transactional_cleanup** should be placed after all your apps. (At
least after those apps which need to remove files.)


## License

django-transactional-cleanup is free software under terms of the MIT License.

Copyright (C) 2012 by Ilya Shalyapin, ishalyapin@gmail.com  
Copyright (C) 2015 by Jesús Espino, jesus.espino@kaleidos.net

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

