"""
Add `django-debug-toolbar`_ to your project to insert a tab on all of your project's HTML pages, which will allow you to track the information on each page, such as the template generation path, the  query arguments received, the number of SQL queries submitted, etc.

This component can only be used in a development or integration environment and is always disabled during production.

Note that its use extends the response time of your pages and can provokes some mysterious bugs (like with syncdb or zinnia) so for the time being, this mods is disabled. So enable it locally for your needs, but never commit its enabled mod and remember to disable it when you have a strange bug.
"""