from djangomaster.conf import settings
from djangomaster.views import MasterView


class MigrationsView(MasterView):
    name = 'migrations'
    label = 'Migrations'
    title = 'Migrations'
    template_name = 'djangomaster/sbadmin/pages/migrations.html'

    def get_context_data(self, **kwargs):
        context = super(MigrationsView, self).get_context_data(**kwargs)
        if settings.SOUTH_IS_INSTALLED:
            context['history_list'] = history_list
        else:
            context['history_list'] = []

        return context

    def get_queryset(self):
        return []


def history_list():
    """
    Based in:
    https://github.com/dmishe/django-south/blob/master/south/management/commands/migrate.py#L108
    """
    from south import migration
    from south.models import MigrationHistory

    ret = {}

    apps = migration.all_migrations()
    labels = [app.app_label() for app in migration.all_migrations()]

    applied_migrations = []
    for mi in MigrationHistory.objects.filter(app_name__in=labels):
        applied_migrations.append('%s.%s' % (mi.app_name, mi.migration))

    for app in apps:
        label = app.app_label()
        ret[label] = []

        for mi in app:
            migration_name = mi.app_label() + "." + mi.name()
            applied = migration_name in applied_migrations
            ret[label].append({'name': mi.name(), 'applied': applied})

    return ret
