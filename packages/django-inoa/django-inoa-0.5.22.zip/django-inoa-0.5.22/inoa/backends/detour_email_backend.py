# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.utils.importlib import import_module
import traceback


class DetourEmailBackend(BaseEmailBackend):
    """
    A wrapper that optionally modifies email destination addresses,
    intended to prevent development servers from sending emails to actual users.
    When active, the list of original recipients will be sent as an attachment in the emails.
    The detour will be skipped when mail_admins() or mail_managers() is found in the call stack.

    The following settings are required.
    An exception will be thrown when the email backend is initialized if they are missing.


    DETOUR_EMAIL_ADDRESS = 'mail@example.com'
    # or
    DETOUR_EMAIL_ADDRESSES = ['person_a@mail.com', 'person_b@mail.com']
    # or
    DETOUR_EMAIL_ADDRESSES = ['Person A <person_a@mail.com>', 'Person B <person_b@mail.com>']
    # or
    DETOUR_EMAIL_ADDRESSES = [('person A', 'person_a@mail.com'), ('person B', 'person_b@mail.com')]
    # All detoured outgoing emails will be modified to use these emails as the destination address.
    # Set to None to disable the backend -- email recipients will not be modified,
    # and the messages will simply be proxied to the actual email backend.


    DETOUR_EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    # The actual email backend that will be used to send emails.

    The following setting is optional:

    DETOUR_EMAIL_PREFIX = 'my instance name'
    # All detoured outgoing emails will have this prefix prepended to their subject,
    # as long as the backend is enabled (i.e. DETOUR_EMAIL_ADDRESS has a non-empty value).
    # Set to "" or None to disable.
    """
    def __init__(self, fail_silently=False, **kwargs):
        super(DetourEmailBackend, self).__init__(fail_silently=fail_silently, **kwargs)
        try:
            if hasattr(settings, 'DETOUR_EMAIL_ADDRESSES'):
                if settings.DETOUR_EMAIL_ADDRESSES is not None and not settings.DETOUR_EMAIL_ADDRESSES:
                    raise AttributeError("Required setting is invalid: DETOUR_EMAIL_ADDRESSES. It must be None or a non-empty list.")
                self.detour_addresses = settings.DETOUR_EMAIL_ADDRESSES
            elif hasattr(settings, 'DETOUR_EMAIL_ADDRESS'):
                if settings.DETOUR_EMAIL_ADDRESS is None:
                    self.detour_addresses = None
                elif not settings.DETOUR_EMAIL_ADDRESS:
                    raise AttributeError("Required setting is invalid: DETOUR_EMAIL_ADDRESS. It must be None or a non-blank string.")
                else:
                    self.detour_addresses = [settings.DETOUR_EMAIL_ADDRESS]
            else:
                raise AttributeError("Required setting is missing: DETOUR_EMAIL_ADDRESS or DETOUR_EMAIL_ADDRESSES")

            # Convert entries in the format ("Full Name", "name@domain.com") to 'Full Name <name@domain.com>'
            if self.detour_addresses:
                self.detour_addresses = [r if isinstance(r, basestring) else (u"%s <%s>" % (r[0], r[1])) for r in self.detour_addresses]


            try:
                backend_name = settings.DETOUR_EMAIL_BACKEND
            except AttributeError:
                raise AttributeError("Required setting is missing: DETOUR_EMAIL_BACKEND")

            try:
                backend_parts = backend_name.rsplit('.', 1)
                backend_class = getattr(import_module(backend_parts[0]), backend_parts[1])
            except Exception as ex:
                raise AttributeError(
                    "Setting DETOUR_EMAIL_BACKEND is invalid or doesn't map to a backend class.\n"
                    "Setting value: %s\nException details: %s" % (backend_name, ex))

            self.actual_backend = backend_class(fail_silently=fail_silently, **kwargs)
            self.failed_silently = False

            subject_prefix = getattr(settings, 'DETOUR_EMAIL_PREFIX', None)
            self.subject_prefix = subject_prefix or u""

        except:
            if fail_silently:
                self.failed_silently = True
            else:
                raise

    def open(self, *args, **kwargs):
        if self.failed_silently:
            return
        return self.actual_backend.open(*args, **kwargs)

    def close(self, *args, **kwargs):
        if self.failed_silently:
            return
        return self.actual_backend.close(*args, **kwargs)

    def send_messages(self, email_messages, *args, **kwargs):
        """
        Sends one or more EmailMessage objects and returns the number of email
        messages sent.
        """
        if self.failed_silently:
            return 0
        if not email_messages:
            return 0
        if self.detour_addresses:
            stack = [item[2] for item in traceback.extract_stack()]
            if not self.skip_detour(stack):
                for message in email_messages:
                    former_to = u", ".join(message.to)
                    former_cc = u", ".join(message.cc)
                    former_bcc = u", ".join(message.bcc)
                    message.to = self.detour_addresses
                    message.subject = u"%s%s" % (self.subject_prefix, message.subject)
                    message.cc = []
                    message.bcc = []
                    original_recipients = (
                        u"Redirected by DetourEmailBackend. Original recipientes below."
                        u"\n----\nTo: %s\nCc: %s\nBcc: %s" % (former_to, former_cc, former_bcc))
                    message.attach("original_recipients.txt", original_recipients, "text/plain;charset='utf8'")
        return self.actual_backend.send_messages(email_messages, *args, **kwargs)

    def skip_detour(self, stack):
        for item in stack:
            if ('mail_admins' in item) or ('mail_managers' in item) or ('send_test_email' in item):
                return True
        return False
