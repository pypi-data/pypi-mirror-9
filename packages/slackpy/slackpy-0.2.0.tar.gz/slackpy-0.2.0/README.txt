slackpy
=======

slackpy is `Slack`_ client library for specific logging.

Install
-------

.. code:: sh

    pip install slackpy

Dependencies
------------

-  requests 2.3

Sample Code
-----------

.. code:: python

    import slackpy

    INCOMING_WEB_HOOK = 'your_web_hook_url'
    CHANNEL = '#general'
    USER_NAME = 'Logger'

    # Create a new instance.
    logging = slackpy.SlackLogger(INCOMING_WEB_HOOK, CHANNEL, USER_NAME)

    # LogLevel: INFO
    logging.info(message='INFO Message')

    # LogLevel: WARN
    logging.warn(message='WARN Message')

    # LogLevel: ERROR
    logging.error(message='ERROR Message')

Correspondence table
~~~~~~~~~~~~~~~~~~~~

+-----------+---------------+--------------------+
| Method    | LogLevel      | Color              |
+===========+===============+====================+
| info()    | INFO (1)      | good (green)       |
+-----------+---------------+--------------------+
| warn()    | WARNING (2)   | warning (orange)   |
+-----------+---------------+--------------------+
| error()   | ERROR (3)     | danger (red)       |
+-----------+---------------+--------------------+

Command line
------------

.. code:: sh

    INCOMING_WEB_HOOK='your_web_hook_url'

    # LogLevel: INFO
    slackpy -c '#your_channel' -m 'INFO Message' -l 1

    # LogLevel: WARN
    slackpy -c '#your_channel' -m 'WARN Message' -l 2

    # LogLevel: ERROR
    slackpy -c '#your_channel' -m 'ERROR Message' -l 3

    # LogLevel: INFO (with Message Title)
    slackpy -c '#your_channel' -t 'Message Title' -m 'INFO Message' -l 1

.. _Slack: https://slack.com

