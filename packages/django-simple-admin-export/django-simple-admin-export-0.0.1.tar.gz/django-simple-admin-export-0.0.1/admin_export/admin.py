
from django.http import HttpResponse
from django.utils.encoding import is_protected_type, force_text
from django.utils.timezone import now

import unicodecsv

def export_field(row, obj, field):
    value = field._get_val_from_obj(obj)
    if is_protected_type(value):
        row.append(value)
    else:
        row.append(field.value_to_string(obj))


def export_fk_field(row, obj, field):
    value = getattr(obj, field.get_attname())
    if not is_protected_type(value):
        value = field.value_to_string(obj)
    row.append(value)


def export_m2m_field(row, obj, field):
    if field.rel.through._meta.auto_created:
        m2m_value = lambda value: force_text(value._get_pk_val(), strings_only=True)
        row.append(','.join(
            [m2m_value(related) for related in getattr(obj, field.name).iterator()]
        ))


def export_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    name = modeladmin.model.__name__
    date = now()
    name = "{}{}".format(name, date.strftime("%Y-%m-%d-%H-%M"))
    response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(name)
    writer = unicodecsv.writer(response)


    for obj in queryset:
        row = []
        concrete_model = obj._meta.concrete_model
        for field in concrete_model._meta.local_fields:
            if field.serialize:
                if field.rel is None:
                    export_field(row, obj, field)
                else:
                    export_fk_field(row, obj, field)

        for field in concrete_model._meta.many_to_many:
            if field.serialize:
                export_m2m_field(row, obj, field)

        writer.writerow(row)

    return response
export_csv.short_description = "Export selected as CSV"

