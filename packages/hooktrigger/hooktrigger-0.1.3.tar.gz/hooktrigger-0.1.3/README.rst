HookTrigger
===========

Run scripts when (e.g. GitHub) webhooks fire.

To install
----------

    $ pip3 install hooktrigger

(you need to make sure pip is running in Python 3, if you can run pip3 this is probably the case).

With defaults
-------------

    $ hooktrigger

Listen on all addresses on port 8000, and run `git pull origin master` when hook triggered

With all flags
--------------

    $ hooktrigger -k -t github -H 127.0.0.1 -p 1234 -d /path/to/dir echo hello

 - Generate and print a new secret
 - Listen for github webhooks
 - Bind to 127.0.0.1:1234
 - When webhook caught and validated, run `echo hello` in the /path/to/dir directory.

See `hooktrigger -h` for more details

Use with GitHub
---------------

Add a webhook with the Payload URL set to be the host and port where HookTrigger is listening.
Make sure you paste the generated secret into the GitHub Secret field.
