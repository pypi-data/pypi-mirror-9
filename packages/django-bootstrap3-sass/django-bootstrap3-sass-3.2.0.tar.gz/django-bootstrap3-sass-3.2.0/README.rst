================
bootstrap3-sass
================

bootstrap3-sass is a simple Django app to conduct Web-based bootstrap3-sass. For each
question, visitors can choose between a fixed number of answers.

Detailed documentation is in the "docs" directory.

Quick start
-----------


0. refere django libsass config first

	https://github.com/torchbox/django-libsass


1. Add "bootstrap3-sass" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'bootstrap3-sass',
    )

2. import the scss directly in your scss file

	@import "bootstrap";
	

3. enjoy it. bootsrap is in your scss project




