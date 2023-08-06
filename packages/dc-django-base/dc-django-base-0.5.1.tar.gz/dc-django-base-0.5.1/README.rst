DC Django Base
==============

Included Libraries
------------------

The following libraries are made available to your application by **dc-django-base**.

**Python Libraries**:

* django-widget-tweaks
* django-allauth
* django-gravatar2
* selenium

**Javascript**

* bootstrap 3.3.2
* jquery 2.1.3
* jquery cookie 1.4.1
* jquery form 3.51

Installation
------------

Settings
````````

Start the site's settings by importing the ``base_settings`` file::

    from dcbase.base_settings import *

Refer to this file to see the complete list of settings that are included by default. The following are settings that your 
site **must** provide:

* BASE_DIR (typically ``os.path.dirname(os.path.dirname(__file__))``)
* SECRET_KEY (source the production key from a secure place, **not** a text file in a public source repository)
* ROOT_URLCONF
* WSGI_APPLICATION
* DATABASES
* EMAIL_BACKEND (consider using ``django.core.mail.backends.console.EmailBackend`` for testing)

Add the site's apps to ``INSTALLED_APPS`` by prepending them to the base apps::

    INSTALLED_APPS = (
        'some_app',
        'allauth.socialaccount.providers.google',
    ) + INSTALLED_APPS

Other "list" settings can be modified in a similar way. 

Because the order of middleware is important it may be required to copy and modify the entire ``MIDDLEWARE_CLASSES`` setting
to inject a new middleware class in the middle of the list.

Multiple Settings
~~~~~~~~~~~~~~~~~

A project often needs to maintain multiple settings files. For example, a project may require different settings for it's
development, staging, and production sites. Follow this pattern to allow easy switching between settings.

First, create a ``settings_common.py`` file. Fill this file with settings that are common to all configurations. Normally,
this file would import ``dcbase.base_settings`` as described above and include settings like ``BASE_DIR``, ``ROOT_URLCONF``,
``INSTALLED_APPS``, etc. For safety, **never** include a setting here that could expose the production site to danger, such as
``SECRET_KEY`` or ``DEBUG = True``.

Create a settings file for each specific configuration. Include the common settings file (e.g. ``from .settings_common import *``)
and add settings that are unique to the specific installation. For example, create a ``settings_dev.py`` for development settings and
``settings_prod.py`` for production settings. This file will normally contain settings like ``SECRET_KEY``, ``DATABASES``,
``ALLOWED_HOSTS``, etc. Be **very** careful how the production settings file is managed and versioned to avoid exposing sensitive
information such as the secret key and database credentials.

Finally, create a symlink to the specific settings file. For example, ``ln -s settings_prod.py settings.py``.

Urls
````

Include the following urls in the site's urlconf::

    url(r'', include('dcbase.urls')),

Templates
`````````

Create a ``base.html`` in the root of your templates directory. Extend ``dcbase/base.html`` and override
blocks that are global to your site. For example::

    {% extends "dcbase/base.html" %}
    
    {% block headerBarBrand %}My Site Brand{% endblock %}
    {% block footerBar %}
        Footer content!
    {% endblock %}

Templates
---------

DC-Base provides templates to override and include.

Base
````

The ``dcbase/base.html`` provides the basic page framework and layout. Provide your site's base template by extending this template
and overriding the following blocks.

- **pageTitle**: title of the page, as it will appear in the browser window's title bar
- **style**: inline CSS to include in the page style tag. you need to include your own enclosing \<style> element.
- **head**: extra content to include in the page head tag. use this to link external css, add meta tags, etc.
- **headerBarBrand**: content for the "brand" link in the upper right, usually the app title or site logo
- **headerBarBrandLink**: target of the "brand" link, usually the app's home page. default is site root.
- **headerBarLeft**: extra nav items (\<li>'s) to include on the left side of the header bar
- **headerBarRight**: extra nav items (\<li>'s) to include on the right side of the header bar
- **content**: the main content of the page. should normally start with a div with class "container" or "container-fluid"
- **footerBar**: content for the footer nav bar
- **script**: any additional scripts or script links the page needs. inline scripts must supply their own enclosing \<script> tag

Narrow Dialog Base
~~~~~~~~~~~~~~~~~~

Extend from ``dcbase/base-narrow-dialog.html`` for any page that is just a single, vertical form or dialog. Override the following
blocks to provide the dialog content:

- **panelHeading**: title of the dialog panel. include any required \<h*> tags.
- **panelType**: the type of panel (e.g. success, danger, etc.). default is "default"
- **panelBody**: content of the dialog panel

Forms
`````

Include ``dcbase/form.html`` or ``dcbase/form-horizontal.html`` to create consistently styled forms. These templates expect a context
variable called ``form``.

Set the ``autofocus`` context variable to the id of a form field which should be automatically focused when the page loads. For example::

    {% include "dcbase/form.html" with autofocus="id_important_field" %}

Template Tags
`````````````

user_tags
~~~~~~~~~

- **{% userNameLink user %}**: insert a link to the given user's profile

User Profiles
-------------

Create app-specific user profile data by following these instructions. 

Create a database model to encapsulate the profile data. Give it a ``OneToOneField`` to the ``User`` model and call it ``user``.

Create a ``ModelForm`` to update the new profile model.

Create a URL to the view that will edit the new profile model. To be consistent with other profile urls it should be in the form
of ``^accounts/profile/edit/CATEGORY/$``, where CATEGORY is unique to your app.  Make sure the url has a name, such as
``account_profile_edit_CATEGORY``.

Create the view for the above URL. The view class should look similar to this::

    @profile_form_view()
    class ProfileEditCATEGORYView(ProfileEditFormView):
        form_class = MyProfileForm
        profile_nav_name = _('Nav Name')
        profile_panel_name = _('Panel Name')
        profile_edit_url = reverse_lazy('account_profile_edit_CATEGORY')
    
    profileEditCATEGORYView = login_required(ProfileEditCATEGORYView.as_view())

The class-level attribute are:

* **profile_nav_name**: the title that will appear on the user profile navigation bar
* **profile_panel_name**: the title that will appear on the panel that holds the form
* **profile_edit_url**: URL to the page that allows editing of this profile model

After these things are done a new pane will appear in the user's profile edit page. This new page will contain the form for the
apps profile model.

New users will automatically get an instance of the new profile model in the database. If this is a new profile model for a site
with existing users then be sure to use a database migration to create an instance for every existing user.

Testing
-------

This project provides several classes with helper methods for testing. These classes are outlined below.

Base Test Case
``````````````

An abstract base test class is provided as `dcbase.tests.BaseTestCase`. This class provides the following methods:

* **randStr**: generate a random string
* **createUser**: create a normal user
* **createAdminUser**: create an admin user
* **createSuperUser**: create a super user
* **expireSession**: expire a session
* **logInAs**: log a user in
* **logout**: logs out the currently logged in user

Unit Testing
````````````

Normal "unit" tests should derive from `dcbase.tests.unit.UnitTestCase`. This class provides the following methods:

* **assertResponseStatusIsOk**
* **assertResponseStatusIsNotFound**
* **assertResponseStatusIsNotAuthorized**

Requires Login Mixin
~~~~~~~~~~~~~~~~~~~~

The `dcbase.tests.unit.view.mixin.RequiresLogin` class is a mixin class for testing views that verifies that the
view requires a logged in user. This mixin tests that:

* An anonymous user is redirected to the log in page
* The view returns status ok for logged in users

This mixin class requires that `self.url` contains the url of the view under test.

Browser Testing
```````````````

Browser testing, using selenium webdriver, is comprised of two main parts. First, a `PageObject` must be created to
represent each page that the tests will interact with. Second, a test case derived from
`dcbase.tests.browser.BrowserTestCase` must be created for the page under test. Each page object and test case has
a property, `browser`, which is the selenium webdriver object for the browser used in the tests.

Page Object
~~~~~~~~~~~

A page object abstracts all interaction with a web page. Tests should never make selenium calls directly. Follow this pattern
to create a page object::

    class ThingDetailPage(PageObject):
        _urlPattern = 'thing:detail'
        _pageName = 'Thing Detail'

The PageObject requires 2 class-level attributes: `_urlPattern` and `_pageName`. The url pattern specifies a named URL pattern
for the page under test. The page name is used for logging purposes.

Create a new instance of a page object by passing it a selenium webdriver instance and any other keyword arguments necessary to
fill in the variables fields of the url pattern. For example::

    page = ThingDetailPage(self.browser, thingId = 123)

When a page object is created it will verify that the browser is currently at the correct URL for the page. A runtime error is
raised if the browser is currently at any other URL.

BrowserTestCase
~~~~~~~~~~~~~~~

The browser test case derives from `BaseTestCase` and provides several other features. Create a new browser test case using this
pattern::

    class TestThingDetail(BrowserTestCase):
        _pageClass = ThingDetailPage
        _requiresLogin = True           # Optional

        def setUp(self):
            thing = create_a_thing()
            self._urlFields['thingId'] = thing.id
            super().setUp()

In the above example `_pageClass` is the class of the PageObject for the page under test. The `_requiresLogin` property tells
the test case that this page requires the user to be logged in.  When a browser test case starts it will launch the browser,
log in a user if required, and then browse to the page represented by the given PageObject. Variable fields for the page object
URL can be provided during the test case's setUp method, as shown above. An instance of the page object is available from a
property called `page`.

By default, `BrowserTestCase` uses the "Chrome" webdriver. Set the `BROWSER` environment variable to the name of a different
webdriver class to change which browser is used to run the tests.
