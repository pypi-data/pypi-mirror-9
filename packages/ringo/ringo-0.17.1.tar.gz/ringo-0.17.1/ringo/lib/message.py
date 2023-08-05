"""Modul for the messanging system in ringo"""
import logging
import os
import pkg_resources
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

from mako.lookup import TemplateLookup
from ringo.lib.helpers.appinfo import get_app_name, get_app_title

log = logging.getLogger(__name__)


class Mailer:
    def __init__(self, request):
        self.mailer = get_mailer(request)
        self.default_sender = request.registry.settings['mail.default_sender']
        settings = request.registry.settings
        if (bool(settings.get('mail.host')) and
           bool(settings.get('mail.default_sender'))):
            self.enabled = True
        else:
            self.enabled = False

    def send(self, mail):
        """Will send and email with the subject and body to the recipient
        from the sender

        :recipient: The recipients mail address
        :sender: The senders mail address
        :subject: String of subject
        :message: Mails body.
        :returns: True or False

        """
        log.debug("Sending from '%s' to '%s'. Subject: %s" % (mail.sender or self.default_sender, mail.recipients, mail.subject))
        message = Message(subject=mail.subject,
                          sender=mail.sender or self.default_sender,
                          recipients=mail.recipients,
                          body=mail.body)
        if self.enabled:
            self.mailer.send(message)
        else:
            log.warning("Sending mail aborted. Mail system not configured")


class Mail:

    def __init__(self, recipients, subject,
                 template=None, values={}, msg="", sender=None):
        self.recipients = recipients
        self.subject = u"[%s] %s" % (get_app_title(), subject)
        self.sender = sender
        self.body = ""

        app_base_dir = pkg_resources.get_distribution(get_app_name()).location
        ringo_base_dir = pkg_resources.get_distribution("ringo").location
        template_dir = os.path.join(app_base_dir,
                                    get_app_name(),
                                    'templates/mails')
        ringo_template_dir = os.path.join(ringo_base_dir,
                                          "ringo",
                                          'templates/mails')
        self.tl = TemplateLookup(directories=[template_dir,
                                              ringo_template_dir])

        if template:
            self.template = self.tl.get_template("%s.mako" % template)
            self.body = self.template.render(**values)
        elif msg:
            self.body = msg
        else:
            raise Exception("Mail is missing either a"
                            " template and values or a msg")
        log.debug(self.body)
