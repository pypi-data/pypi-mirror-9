from __future__ import unicode_literals
from django.contrib import admin
from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils.html import format_html
from dddp import models


def object_admin_link(obj):
    kwargs = {
        'format_string': u'{app_label}.{model} {object_id}: {object}',
        'app_label': obj.content_type.app_label,
        'model': obj.content_type.model,
        'object_id': obj.object_id,
        'object': obj.content_type.model_class().objects.get(pk=obj.object_id),
    }
    try:
        kwargs.update(
            url=reverse(
                'admin:%s_%s_change' % (
                    obj.content_type.app_label,
                    obj.content_type.model,
                ),
                args=(obj.object_id,),
            ),
            format_string='<a href="{url}">%s</a>' % kwargs['format_string'],
        )
    except NoReverseMatch:
        pass
    return format_html(**kwargs)
object_admin_link.short_description = 'Object'
object_admin_link.allow_tags = True


class ObjectMapping(admin.ModelAdmin):
    search_fields = [
        'meteor_id',
    ]
    list_display = [
        'meteor_id',
        object_admin_link,
        'content_type',
        'object_id',
    ]
    list_filter = [
        'content_type__app_label',
        'content_type',
    ]
    list_select_related = [
        'content_type',
    ]


class SubscriptionCollectionInline(admin.TabularInline):
    model = models.SubscriptionCollection
    fields = [
        'collection_class',
    ]
    readonly_fields = [
        'name',
        'collection_class',
    ]
    max_num = 0


class Subscription(admin.ModelAdmin):
    search_fields = [
        'sub_id',
        'publication',
        'publication_class',
        'params_ejson',
    ]
    list_display = [
        'sub_id',
        'connection',
        'user',
        'publication',
        'params_ejson',
    ]
    list_filter = [
        'user__email',
        'publication',
    ]
    inlines = [
        SubscriptionCollectionInline,
    ]


class SubscriptionCollection(admin.ModelAdmin):
    search_fields = [
        'name',
        'collection_class',
    ]
    list_display = [
        '__str__',
        'subscription',
        'name',
        'collection_class',
    ]
    list_filter = [
        'name',
    ]


for name, attr in vars(models).items():
    if hasattr(attr, '_meta'):
        model_admin = locals().get(name, None)
        if model_admin is not False:
            admin.site.register(attr, model_admin)
