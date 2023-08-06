# Copyright (C) 2015, Availab.io(R) Ltd. All rights reserved.
from flask_mail import Message
from webcommon.utils.async_attribute import async


class Mailer:

    def __init__(self, mail, app):
        """
        Constructor

        Args:
            mail: Flask mail instance
            app: Flask app instance

        Returns:
            class instance
        """
        self.mail = mail
        self.app = app
        pass

    @async
    def _send_email_async(self, flask_app, msg):
        """
        Helper method for async email sending
        Args:
            app: Flask app instance
            msg: Flask message instance
        """
        with flask_app.app_context():
            self.mail.send(msg)

    def send_email_async(self, subject, sender, recipients, text_body, html_body):
        """
        Method to send email asynchronously

        Args:

        subject: email subject
        sender:  email sender
        recipients: list of email recipients
        text_body: text content of the email (set none if not needed)
        html_body: html content of the email (set none if not needed)
        """
        msg = self._compose_message(subject, sender, recipients, text_body, html_body)
        self._send_email_async(self.app, msg)

    def send_email(self, subject, sender, recipients, text_body, html_body):
        """
        Method to send email

        Args:
            subject: email subject
            sender:  email sender
            recipients: list of email recipients
            text_body: text content of the email (set none if not needed)
            html_body: html content of the email (set none if not needed)
        """
        msg = self._compose_message(subject, sender, recipients, text_body, html_body)
        self.mail.send(msg)

    @staticmethod
    def _compose_message(subject, sender, recipients, text_body, html_body):
        """
        Helper method for composing email message

        Args:
            subject: email subject
            sender:  email sender
            recipients: list of email recipients
            text_body: text content of the email (set none if not needed)
            html_body: html content of the email (set none if not needed)

        Returns:
            Instance of Flask Message
        """
        msg = Message(subject, sender=sender, recipients=recipients)
        msg.body = text_body
        msg.html = html_body
        return msg