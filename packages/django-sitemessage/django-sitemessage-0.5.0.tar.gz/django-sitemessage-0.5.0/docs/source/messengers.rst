Messengers
==========


`sitemessage` messenger classes implement clients for various protocols (smtp, jabber, etc.).

You can either use builtin classes or define your own.


Helper functions
----------------

* **sitemessage.toolbox.register_messenger_objects(\*messengers)**

  Registers (configures) messengers.

* **sitemessage.toolbox.get_registered_messenger_objects()**

  Returns registered (configured) messengers dict indexed by messenger aliases.

* **sitemessage.toolbox.get_registered_messenger_object(messenger)**

  Returns registered (configured) messenger by alias,



Builtin messengers
------------------

Builtin messengers are available from **sitemessage.messengers**:


* **sitemessage.messengers.smtp.SMTPMessenger**

.. warning::

    Uses Python's built-in ``smtplib``.



* **sitemessage.messengers.xmpp.XMPPSleekMessenger**

.. warning::

    Requires ``sleekxmpp`` package.

.. code-block:: python

    from sitemessage.toolbox import schedule_messages, recipients


    # Sending jabber message.
    schedule_messages('Hello there!', recipients('xmppsleek', 'somebody@example.ru'))



* **sitemessage.messengers.twitter.TwitterMessenger**

.. warning::

    Requires ``twitter`` package.

.. code-block:: python

    from sitemessage.toolbox import schedule_messages, recipients


    # Twitting example.
    schedule_messages('My tweet.', recipients('twitter', ''))

    # Tweet to somebody.
    schedule_messages('Hey, that is my tweet for you.', recipients('twitter', 'idlesign'))



Sending test messages
---------------------

After a messenger is configured you can try whether it works properly using its **send_test_message** method:

.. code-block:: python

    from sitemessage.messengers.smtp import SMTPMessenger


    msgr = SMTPMessenger('user1@host.com', 'user1', 'user1password', host='smtp.host.com', use_tls=True)
    msgr.send_test_message('user1@host.com', 'This is a test message')



User defined messengers
-----------------------

To define a message type one needs to inherit from **sitemessage.messengers.base.MessengerBase** (or a builtin messenger class),
and to register it with **sitemessage.toolbox.register_messenger_objects** (put these instructions
into `sitemessages.py` in one of your apps):


.. code-block:: python

    from sitemessage.messengers.base import MessengerBase
    from sitemessage.toolbox import register_messenger_objects


    class MyMessenger(MessengerBase):

        # Messengers could be addressed by aliases.
        alias = 'mymessenger'

        # Messenger title to show up in UI
        title = 'Super messenger'

        def __init__(self):
            """This messenger doesn't accept any configuration arguments.
            Other may expect login, password, host, etc. to connect this messenger to a service.

            """
        @classmethod
        def get_address(cls, recipient):
            address = recipient
            if hasattr(recipient, 'username'):
                # We'll simply get address from User object `username`.
                address = '%s--address' % recipient.username
            return address

    def before_send(self):
        """We don't need that for now, but usually here will be messenger warm up (connect) code."""

    def after_send(self):
        """We don't need that for now, but usually here will be messenger cool down (disconnect) code."""

    def send(self, message_cls, message_model, dispatch_models):
        """This is the main sending method that every messenger must implement."""

        # `dispatch_models` from sitemessage are models representing a dispatch
        # of a certain message_model for a definite addressee.
        for dispatch_model in dispatch_models:

            # For demonstration purposes we won't send a dispatch anywhere,
            # we'll just mark it as sent:
            self.mark_sent(dispatch_model)  # See also: self.mark_failed() and self.mark_error().

    register_messenger_objects(MyMessenger())


.. note::

    Look through ``MessengerBase`` and other builtin messenger classes for more information and
    code examples.


After that you can schedule and send messages with your messenger as usual:

.. code-block:: python

    from sitemessage.toolbox import schedule_messages, recipients


    user2 = ...  # Let's suppose it's an instance of Django user model.
    # We'll just try to send PlainText message.
    schedule_messages('Some plain text message', recipients('mymessenger', ['user1--address', user2]))
