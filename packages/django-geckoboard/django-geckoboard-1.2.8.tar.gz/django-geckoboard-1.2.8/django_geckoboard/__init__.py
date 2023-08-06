"""
=================
django-geckoboard
=================

Geckoboard_ is a hosted, real-time status board serving up indicators
from web analytics, CRM, support, infrastructure, project management,
sales, etc.  It can be connected to virtually any source of quantitative
data.  This Django_ application provides view decorators to help create
custom widgets.

.. _Geckoboard: http://www.geckoboard.com/
.. _Django: http://www.djangoproject.com/


Installation
============

To install django-geckoboard, simply place the ``django_geckoboard``
package somewhere on the Python path.  You do not need to add it to the
``INSTALLED_APPS`` list, unless you want to run the tests.


Limiting access
===============

If you want to protect the data you send to Geckoboard from access by
others, you can use an API key shared by Geckoboard and your widget
views.  Set ``GECKOBOARD_API_KEY`` in the project ``settings.py`` file::

    GECKOBOARD_API_KEY = 'XXXXXXXXX'

If you do not set an API key, anyone will be able to view the data by
visiting the widget URL.


Encryption
==========

Geckoboard encryption allows encrypting data before it is sent to Geckoboard's
servers. After entering the password used to encrypt the data when the Geckoboard
is loaded, the data will be decrypted in the browser.

To use encryption, first set a password in the project ``settings.py`` file::

    GECKOBOARD_PASSWORD = 'XXXXXXXXX'

Next, enable encryption for each widget using the decorator arguments::

    @number_widget(encrypted=True)
        def user_count(request):
            return User.objects.count()


Creating custom widgets
=======================

The available custom widgets are described in the Geckoboard support
section, under `Geckoboard API`_.  From the perspective of a Django
project, a custom widget is just a view.  The django-geckoboard
application provides view decorators that render the correct response
for the different widgets.

Let's say you want to add a widget to your dashboard that shows the
number of number of comments posted today.  First create a view, using a
django-geckoboard decorator::

    from datetime import date, time, datetime
    from django.contrib.comments.models import Comment
    from django_geckoboard.decorators import number_widget

    @number_widget
    def comment_count(request):
        midnight = datetime.combine(date.today(), time.min)
        return Comment.objects.filter(submit_date__gte=midnight).count()

You can also specify the output format of the widget as either JSON or XML::

   @number_widget(format='json')
   def comment_count(request):
        midnight = datatime.combine(date.today(), time.min)
        return Comment.objects.filter(submit_data__get=midnight).count()


If your widget has optional settings, you can pass them in the decorator
definition::

    @number_widget(absolute='true')
    def comment_count(request):
        midnight = datetime.combine(date.today(), time.min)
        return Comment.objects.filter(submit_date__gte=midnight).count()


Then use a URLconf module to map a URL to the view::

    from django.conf.urls.defaults import *

    urlpatterns = patterns('YOUR_VIEW_MODULE',
        ...
        (r'^geckoboard/comment_count/$', 'comment_count'),
    )

This is all the Django code you need to display the comment count on
your dashboard. When you create a custom widget in Geckoboard, enter the
following information:

Encryption
    Enable if the field is encrypted (see instructions above).

URL data feed
    The view URL.  In the example above this would be something like
    ``http://HOSTNAME/geckoboard/comment_count/``.

API key
    The content of the ``GECKOBOARD_API_KEY`` setting, if you have set
    it.

Widget type
    *Custom*

Feed format
    Either *XML* or *JSON*.  If you don't specify a format the decorators will
    automatically detect and output the correct format or default to XML
    if this is not enabled (by default the format isn't appended by
    Geckoboard as a parameter any more)

Request type
    Either *GET* or *POST*.  The view decorators accept both.


The following decorators are available from the
``django_geckoboard.decorators`` module:


``number_widget``
-----------------

Render a *Number & Secondary Stat* widget.

The decorated view must return a tuple *(current, [previous],
[prefix])* where the *current* parameter is the current value, optional
*previous* parameter is the previous value of the measured quantity and
the optional parameter *prefix* is the prefix used in Geckoboard widget.
If there is only one parameter you do not need to return it in a tuple.
For example, to render a widget that shows the number of users and the
difference from last week::

    from django_geckoboard.decorators import number_widget
    from datetime import datetime, timedelta
    from django.contrib.auth.models import User

    @number_widget
    def user_count(request):
        last_week = datetime.now() - timedelta(weeks=1)
        users = User.objects
        last_week_users = users.filter(date_joined__lt=last_week)
        return (users.count(), last_week_users.count())

    @number_widget
    def users_count_with_prefix(request):
        last_week = datetime.now() - timedelta(weeks=1)
        users = User.objects
        last_week_users = users.filter(date_joined__lt=last_week)
        return (users.count(), last_week_users.count(), '$')


``rag_widget``
--------------

Render a *RAG Column & Numbers* or *RAG Numbers* widget.

The decorated view must return a tuple with three tuples *(value,
[text])*.  The *value* parameters are the numbers shown in red, amber
and green (in that order).  The optional *text* parameters will be
displayed next to the respective values in the dashboard.

For example, to render a widget that shows the number of comments that
were approved or deleted by moderators in the last 24 hours::

    from django_geckoboard.decorators import rag_widget
    from datetime import datetime, timedelta
    from django.contrib.comments.models import Comment, CommentFlag

    @rag_widget
    def comments(request):
        start_time = datetime.now() - timedelta(hours=24)
        comments = Comment.objects.filter(submit_date__gt=start_time)
        total_count = comments.count()
        approved_count = comments.filter(
                flags__flag=CommentFlag.MODERATOR_APPROVAL).count()
        deleted_count = Comment.objects.filter(
                flags__flag=CommentFlag.MODERATOR_DELETION).count()
        pending_count = total_count - approved_count - deleted_count
        return (
            (deleted_count, "Deleted comments"),
            (pending_count, "Pending comments"),
            (approved_count, "Approved comments"),
        )


``text_widget``
---------------

Render a *Text* widget.

The decorated view must return a list of tuples *(message, [type])*.
The *message* parameters are strings that will be shown in the widget.
The *type* parameters are optional and tell Geckoboard how to annotate
the messages.  Use ``TEXT_INFO`` for informational messages,
``TEXT_WARN`` for for warnings and ``TEXT_NONE`` for plain text (the
default).  If there is only one plain message, you can just return it
without enclosing it in a list and tuple.

For example, to render a widget showing the latest Geckoboard twitter
updates, using Mike Verdone's `Twitter library`_::

    from django_geckoboard.decorators import text_widget, TEXT_NONE
    import twitter

    @text_widget
    def twitter_status(request):
        twitter = twitter.Api()
        updates = twitter.GetUserTimeline('geckoboard')
        return [(u.text, TEXT_NONE) for u in updates]

.. _`Twitter library`: http://pypi.python.org/pypi/twitter


``pie_chart``
-------------

Render a *Pie chart* widget.

The decorated view must return an iterable over tuples *(value, label,
[color])*.  The optional *color* parameter is a string ``'RRGGBB[TT]'``
representing red, green, blue and optionally transparency.

For example, to render a widget showing the number of normal, staff and
superusers::

    from django_geckoboard.decorators import pie_chart
    from django.contrib.auth.models import User

    @pie_chart
    def user_types(request):
        users = User.objects.filter(is_active=True)
        total_count = users.count()
        superuser_count = users.filter(is_superuser=True).count()
        staff_count = users.filter(is_staff=True,
                                   is_superuser=False).count()
        normal_count = total_count = superuser_count - staff_count
        return [
            (normal_count,    "Normal users", "ff8800"),
            (staff_count,     "Staff",        "00ff88"),
            (superuser_count, "Superusers",   "8800ff"),
        ]


``line_chart``
--------------

Render a *Line chart* widget.

The decorated view must return a tuple *(values, x_axis, y_axis,
[color])*.  The *values* parameter is a list of data points.  The
*x-axis* parameter is a label string or a list of strings, that will be
placed on the X-axis.  The *y-axis* parameter works similarly for the
Y-axis.  If there are more than one axis label, they are placed evenly
along the axis.  The optional *color* parameter is a string
``'RRGGBB[TT]'`` representing red, green, blue and optionally
transparency.

For example, to render a widget showing the number of comments per day
over the last four weeks (including today)::

    from django_geckoboard.decorators import line_chart
    from datetime import date, timedelta
    from django.contrib.comments.models import Comment

    @line_chart
    def comment_trend(request):
        since = date.today() - timedelta(days=29)
        days = dict((since + timedelta(days=d), 0)
                for d in range(0, 29))
        comments = Comment.objects.filter(submit_date__gte=since)
        for comment in comments:
            days[comment.submit_date.date()] += 1
        return (
            days.values(),
            [days[i] for i in range(0, 29, 7)],
            "Comments",
        )


``geck_o_meter``
----------------

Render a *Geck-O-Meter* widget.

The decorated view must return a tuple *(value, min, max)*.  The *value*
parameter represents the current value.  The *min* and *max* parameters
represent the minimum and maximum value respectively.  They are either a
value, or a tuple *(value, text)*.  If used, the *text* parameter will
be displayed next to the minimum or maximum value.

For example, to render a widget showing the number of users that have
logged in in the last 24 hours::

    from django_geckoboard.decorators import geck_o_meter
    from datetime import datetime, timedelta
    from django.contrib.auth.models import User

    @geck_o_meter
    def login_count(request):
        since = datetime.now() - timedelta(hours=24)
        users = User.objects.filter(is_active=True)
        total_count = users.count()
        logged_in_count = users.filter(last_login__gt=since).count()
        return (logged_in_count, 0, total_count)


``funnel``
----------

Render a *Funnel* widget.

The decorated view must return a dictionary with at least an *items*
key.  To render a funnel showing the breakdown of authenticated users
vs. anonymous users::

    from django_geckoboard.decorators import funnel
    from django.contrib.auth.models import User

    @funnel
    def user_breakdown(request):
        all_users = User.objects
        active_users =all_users.filter(is_active=True)
        staff_users = all_users.filter(is_staff=True)
        super_users = all_users.filter(is_superuser=True)
        return {
            "items": [
                (all_users.count(), 'All users'),
                (active_users.count(), 'Active users'),
                (staff_users.count(), 'Staff users'),
                (super_users.count(), 'Super users'),
            ],
            "type": "standard",   # default, 'reverse' changes direction
                                  # of the colors.
            "percentage": "show", # default, 'hide' hides the percentage
                                  # values.
            "sort": False,        # default, `True` orders the values
                                  # descending.
        }

``bullet``
----------

Render a *Bullet* widget.

The decorated view must return a dictionary with at least keys *label*,
*axis_points*, *current* and *comparative*. To render Geckoboard's own example
at
http://support.geckoboard.com/entries/274940-custom-chart-widget-type-definitions::

    from django_geckoboard.decorators import bullet

    @bullet
    def geckoboard_bullet_example(request):
        return = {
            'label': 'Revenue 2011 YTD',
            'axis_points': [0, 200, 400, 600, 800, 1000],
            'current': 500,
            'comparative': 600,
            'sublabel': 'U.S. $ in thousands',
            'red': [0, 400],
            'amber': [401, 700],
            'green': [701, 1000],
            'projected': [100, 900],
            'auto_scale': False,
        }

.. _`Geckoboard API`: http://geckoboard.zendesk.com/forums/207979-geckoboard-api
"""

__author__ = "Joost Cassee"
__email__ = "joost@cassee.net"
__version__ = "1.2.8"
__copyright__ = "Copyright (C) 2011-2013 Joost Cassee and others"
__license__ = "MIT License"
