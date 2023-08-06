from .messages.email import EmailHtmlMessage, EmailTextMessage
from .toolbox import schedule_messages, recipients
from .settings import DEFAULT_SHORTCUT_EMAIL_MESSAGES_TYPE


def schedule_email(message, to, subject=None, sender=None, priority=None):
    """Schedules an email message for delivery.

    :param dict, str message: str or dict: use str for simple text email;
        dict - to compile email from a template (default: `sitemessage/messages/email_html__smtp.html`).
    :param list to: recipients addresses or Django User model heir instances
    :param str subject: email subject
    :param User sender: User model heir instance
    :param int priority: number describing message priority. If set overrides priority provided with message type.
    """
    if isinstance(message, dict):
        message_cls = EmailHtmlMessage
    else:
        message_cls = EmailTextMessage

    schedule_messages(
        message_cls(subject, message),
        recipients(DEFAULT_SHORTCUT_EMAIL_MESSAGES_TYPE, to),
        sender=sender, priority=priority
    )


def schedule_jabber_message(message, to, sender=None, priority=None):
    """Schedules an email message for delivery.

    :param str message: text to send.
    :param list to: recipients addresses or Django User model heir instances
    :param User sender: User model heir instance
    :param int priority: number describing message priority. If set overrides priority provided with message type.
    """
    schedule_messages(message, recipients('xmppsleek', to), sender=sender, priority=priority)
