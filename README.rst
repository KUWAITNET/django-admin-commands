
Django-admin-commands
=====================

Sometimes one would like to allow the admin to have access to some of the management commands.
djagno-admin-commands2 is the answer. A Tool to execute management commands from admin with ease and control.


Features
--------

* Specify the commands you need to allow for admin to execute. (Or explicitly choose all)
* Get the logs out in admin
* Easily customizable to use django-rq or other queueing technique


Installation
------------
* Use the package manager `pip <https://pip.pypa.io/en/stable/>`_ to install django-admin-commands2.
  *There was a package with the same name on pypi , hence the 2 suffix*

.. code-block:: console

        pip install django-admin-commands2

* Add admin_commands to you INSTALLED_APPS

* python manage.py migrate



Usage
-----
* Adds the commands you need to allow to the admin. Example:

.. code-block:: python

        ADMIN_COMMANDS_CONFIG = {
                'allowed_commands': ['ping_google', 'update_index']
                # OR
                # 'allowed_commands': 'all'
                # this will load all the commands available on manage.py
        }

* Navigate to the admin site `/admin_commands/managementcommands/` to find the commands you have allowed added

Permissions
-----------
App comes with 2 permissions
1. `Can execute management commands` which is required to access & execute commands allowed.
2. `View other users log` which is allow the user to see the logs of other users ran commands.



Customization
-------------
You can override the admin class for ManagementCommandsAdmin to customize the admin view.

.. code-block:: python

        from admin_commands.admin import CommandAdminBase, ManagementCommandAdmin
        from admin_commands.models import ManagementCommands

        class CustomManagementCommandsAdmin(ManagementCommandAdmin):

            def execute_command_and_return_response(self, request, command, args):
                # Easy Entry point to customize execution, maybe wrap it in a django rq job or something :
                import django_rq
                django_rq.enqueue(command.execute, request.user, args)
                # Current implementation is:
                command.execute(request.user, args)

                self.message_user(request, _('Command executed'))
                return self.response_post_save_add(request, command)

            def execute_command_view(self, request, object_id):
                # This is the view that is called when the user clicks on the execute button, you can override this to
                # customize the execution of the command, check source for information on how to do this.
                pass

        admin.site.unregister(ManagementCommands)
        admin.site.register(ManagementCommands, CustomManagementCommandsAdmin)

