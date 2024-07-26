from django.contrib import admin, messages
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from mailer.engine import send_all
from mailer.models import DontSendEntry, Message, MessageLog


class MessageAdminMixin:

    def _body(self, instance, type):
        email = instance.email

        body = email.get_body(
                preferencelist=(type, )
            )
        if not body:
            return "<Can't decode>"

        return body

    def plain_text_body(self, instance):
        return self._body(instance, 'plain')

    def html_body(self, instance):
        return mark_safe(self._body(instance, 'html'))

    def related_body(self, instance):
        return self._body(instance, 'related')


class MessageAdmin(MessageAdminMixin, admin.ModelAdmin):

    list_display = ["id", "show_to", "subject", "when_added", "priority", "retry_count"]
    readonly_fields = ["plain_text_body", "html_body", "related_body"]
    date_hierarchy = "when_added"
    actions = ["send_messages"]

    def send_messages(self, request, queryset):
        send_all(queryset)
        messages.add_message(request, messages.INFO, _("Message(s) sent."))


class DontSendEntryAdmin(admin.ModelAdmin):

    list_display = ["to_address", "when_added"]


class MessageLogAdmin(MessageAdminMixin, admin.ModelAdmin):

    list_display = ["id", "show_to", "show_subject", "message_id", "when_attempted", "result"]
    list_filter = ["result"]
    date_hierarchy = "when_attempted"
    readonly_fields = ["plain_text_body", "message_id"]
    search_fields = ["message_id"]


admin.site.register(Message, MessageAdmin)
admin.site.register(DontSendEntry, DontSendEntryAdmin)
admin.site.register(MessageLog, MessageLogAdmin)
