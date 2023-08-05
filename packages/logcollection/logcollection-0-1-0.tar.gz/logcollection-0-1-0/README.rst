logcollection

logging handler collection

install
===========

Next, execute command.::

    $ pip install logcollection


How to use
===========

logger configuration file example

::

    [loggers]
    keys = root

    [handlers]
    keys = console, slack_webhook, slack_api, hipchat

    [formatters]
    keys = generic

    [logger_root]
    level = DEBUG
    handlers = console, slack_webhook, slack_api, hipchat
    qualname = TESTLOGG
    propagate = 0

    [handler_console]
    class = StreamHandler
    level = DEBUG
    formatter = generic
    args = (sys.stdout,)

    [handler_slack_webhook]
    class = logcollection.LogCollectionHandler
    level = DEBUG
    formatter = generic
    args = ('logcollection.SlackIncomingWebHookSender', 'domain.slack.com', '#random', 'username')

    [handler_slack_api]
    class = logcollection.LogCollectionHandler
    level = DEBUG
    formatter = generic
    args = ('logcollection.SlackAPIChatPostMessageSender', '#random', 'username')

    [handler_hipchat]
    class = logcollection.LogCollectionHandler
    level = DEBUG
    formatter = generic
    args = ('logcollection.HipChatSender', 'token', 'room_id')

    [formatter_generic]
    format = %(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s
    datefmt =
