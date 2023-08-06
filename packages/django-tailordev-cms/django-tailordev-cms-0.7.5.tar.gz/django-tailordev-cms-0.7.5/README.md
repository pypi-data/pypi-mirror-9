TailorDev CMS
=============

A simple CMS for your django projects.

## Dependencies

For now, Django>=1.5 is required for this project to run on production, with python>=2.6. Currently, this application is not compatible with python 3.3. We are working on it.

This CMS is a simple application that generously takes advantage of the following django packages:

* django-grappelli: sexy admin rendering with TinyMCE rich text editor (this should not be a dependency for further releases)
* django-reversion: track article edition history
* django-modeltranslation: articles internationalization
* django-mptt: article categories hierarchy

## Installation

To install TailorDev CMS, use pip:

    $ pip install django-tailordev-cms

If you intend to test or improve this application, first clone this repository and install the local dependencies:

    $ pip install -r requirements/local.txt

Add `td_cms` and its dependencies to your `INSTALLED_APPS`:

    INSTALLED_APPS = (
    ...
        # CMS
        'grappelli',
        'reversion',
        'modeltranslation',
        'mptt',
        'td_cms',
    ...
    )

Add `td_cms` urls to your project url patterns:

    urlpatterns = patterns('',
        ...
        url(r'', include('td_cms.urls')),  # should be last
    )

> Note due to default url patterns `/category-slug/page-slug/`, we strongly recommand to include td_cms url patterns after all other patterns.

And then update your database:

    $ python manage.py syncdb
    $ python manage.py migrate

Create the filemanager upload directory (replace the {{ MEDIA_ROOT }} by your setting value):

    $ mkdir -p {{ MEDIA_ROOT }}/uploads/images/pages

## Templates

Create a base template to inherit from. It should be visible as `_layouts/base.html`

NB: to load td_cms styles, ensure your base template has a `css` block.

## Running the Tests

You can run the tests with via:

    $ python setup.py test

or:

    $ python runtests.py
