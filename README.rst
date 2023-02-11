Django-admin-commands
=====================

Because sometimes you want to give teh admin access to some commands. This app allows you to specify the commands you want to allow the admin to execute. It also logs the commands executed and the output of the command.

Features
--------

* Specify the commands you need to allow for admin to execute. (Or explicitly choose all)
* Get the logs, stdout, stderr in admin.
* Easy permissions
* Easily customizable to use django-rq or other queueing technique


Installation
------------

* Install directly from repo

.. code-block:: console

        pip install git+https://github.com/RamezIssac/django-admin-commands#egg=django-admin-commands


(not yet) Use the package manager `pip <https://pip.pypa.io/en/stable/>`_ to install django-admin-commands2.
*There is a package with the same name on pypi , hence the 2 suffix*

.. code-block:: console

        pip install django-admin-commands2

* Add `admin_commands` to your `INSTALLED_APPS`

* python manage.py migrate



Usage
-----
* Adds the commands you need to allow to the admin to your settings. Example:

.. code-block:: python

        # settings.py
        ADMIN_COMMANDS_CONFIG = {
                'allowed_commands': [
                    'ping_google', # command name
                    ('update_index', '--no-input') # you can also pass arguments to the command,
                    ]
                # You can also use the following to allow all commands
                # 'allowed_commands': 'all'
        }

* Navigate to the admin site and you will see a new section called `Management Commands` with commands to execute and see their logs

Permissions
-----------
App comes with 2 permissions

1. `Can execute management commands` which is required to access & execute commands allowed.
2. `View other users log` which is allow the user to see the logs of other users ran commands. If Not given, logs will be filtered to own records only.



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

            def get_queryset(self, request):
                # This is the queryset that is used to filter the commands that are shown in the admin.
                # You can override this to customize the queryset for the user
                pass

        admin.site.unregister(ManagementCommands)
        admin.site.register(ManagementCommands, CustomManagementCommandsAdmin)

