# -*- coding: utf-8 -*-
from django.core.mail.message import EmailMessage
from django.core.management.base import BaseCommand
from optparse import make_option


class Command(BaseCommand):
    help = \
u"""Send a test email to one or more recipients."""
    args = 'recipient [recipient ...]'

    option_list = BaseCommand.option_list + (
        make_option('--subject',
            action='store',
            dest='subject',
            default=None,
            help="Specify the email subject"),
        make_option('--body',
            action='store',
            dest='body',
            default=None,
            help="Specify the email body"),
    )

    def handle(self, *args, **options):
        recipients = args

        if not recipients:
            self.stderr.write(u"At least one recipient must be informed.")
            return
        subject = options.get('subject') or u"Django test email"
        body = options.get('body') or u"This is a test email to verify if the Django email settings are correct.\n\nIf you are reading this, it has succeeded!"

        result = self.send_test_email(subject, body, recipients)
        if result:
            self.stdout.write(u"Message sent successfully. Please check your inbox.")
        else:
            self.stderr.write(u"Failure while sending message. Verify the email settings in Django.")

            
    def send_test_email(self, subject, body, recipients):
        msg = EmailMessage(subject=subject, body=body, to=recipients)
        return msg.send()
