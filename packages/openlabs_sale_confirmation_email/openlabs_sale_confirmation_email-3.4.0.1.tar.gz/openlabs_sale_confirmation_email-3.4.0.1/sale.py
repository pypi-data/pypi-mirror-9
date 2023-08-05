# -*- coding: utf-8 -*-
"""
    sale.py

    :copyright: (c) 2015 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import PoolMeta, Pool
from trytond.model import Workflow, ModelView, fields
from trytond.config import config
from trytond.report import Report

__all__ = ['Sale']
__metaclass__ = PoolMeta


class Sale:
    __name__ = 'sale.sale'

    email_sent = fields.Boolean('Confirmation Email Sent?', readonly="True")

    def send_confirmation_email(self):
        """
        An email confirming that the order has been confirmed and that we are
        waiting for the payment confirmation if we are really waiting for it.

        For setting a convention this email has to be sent by rendering the
        templates
           * Text: `<module_name>/emails/sale-confirmation-text.jinja`
           * HTML: `<module_name>/emails/sale-confirmation-html.jinja`
        """
        EmailQueue = Pool().get('email.queue')
        ModelData = Pool().get('ir.model.data')
        Group = Pool().get('res.group')
        Sale = Pool().get('sale.sale')
        Mail = Pool().get('mail.mail')

        if self.email_sent:
            return

        group_id = ModelData.get_id(
            "sale_confirmation_email", "order_confirmation_receivers"
        )
        bcc_emails = map(
            lambda user: user.email,
            filter(lambda user: user.email, Group(group_id).users)
        )

        to_emails = self._get_receiver_email_address()
        if to_emails:
            sender = config.get('email', 'from')
            subject = self._get_subject_for_email()
            html_template, text_template = self._get_email_template_paths()
            template_context = self._get_email_template_context()

            email_message = Mail.render_email(
                from_email=sender,
                to=', '.join(to_emails),
                subject=subject,
                text_template=text_template,
                html_template=html_template,
                sale=self,
                **template_context
            )

            EmailQueue.queue_mail(
                sender, to_emails + bcc_emails,
                email_message.as_string()
            )

            Sale.write([self], {
                'email_sent': True,
            })

    def _get_subject_for_email(self):
        """
        Returns the subject for order confirmation email

        Downstream modules can override this method to change subject
        """
        return "Order Confirmed #%s" % self.reference

    def _get_receiver_email_address(self):
        """
        Returns a list of sale party emails to send email to

        Downstream modules can modify this method to return the email
        addresses of sale party
        """
        return self.party.email and [self.party.email] or []

    def _get_email_template_paths(self):
        """
        Returns a tuple of the form:
        (html_template, text_template)
        """
        return (
            'sale_confirmation_email/emails/sale-confirmation-html.html',
            'sale_confirmation_email/emails/sale-confirmation-text.html'
        )

    def _get_email_template_context(self):
        """
        Add to email template context
        """
        return {
            'formatLang': lambda *args, **kargs: Report.format_lang(
                *args, **kargs)
        }

    @classmethod
    @ModelView.button
    @Workflow.transition('confirmed')
    def confirm(cls, sales):
        """
        Send an email after sale is confirmed
        """
        super(Sale, cls).confirm(sales)

        for sale in sales:
            sale.send_confirmation_email()
