"""
Enable `Django registration`_ and everything you need to allow users to request registration and to connect/disconnect. The views and forms are added so this part can be used. 

It includes:

* A view for the login and one for the logout;
* All the views for the registration request (request, confirmation, etc.);
* A view to ask for the reinitialization of a password.

In the ``skeleton.html`` template, a partial HTML code is commented. Uncomment it to display the *logout* button when the user is connected.

The registration process consists in sending an email (to be configured in the settings) with the registration request to an administrator responsible for accepting them (or not). Once validated, an email is sent to the user to confirm his registration by way of a link. Once this step has been completed, the user can connect.
"""