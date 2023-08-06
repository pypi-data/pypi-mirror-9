from django.db.models import Manager as Manager
from django_permanent import settings


class M2MPermanentManager(Manager):
    """Manager provides consistent m2m with through"""

    def get_queryset(self, *args, **kwargs):
        from django_permanent.models import PermanentModel
        if self.__class__.__name__ == 'ManyRelatedManager' and issubclass(self.through, PermanentModel):
            self.core_filters['%s__%s' % (self.source_field.related_query_name(), settings.FIELD)] = None
        return super(M2MPermanentManager, self).get_queryset(*args, **kwargs)


def QuerySetManager(qs):
    class QuerySetManager(M2MPermanentManager, Manager):
        qs_class = qs
        use_for_related_fields = True

        def get_queryset(self):
            return self.qs_class(self.model, using=self._db)

        def get_restore_or_create(self, *args, **kwargs):
            return self.get_queryset().get_restore_or_create(*args, **kwargs)

        def restore(self, *args, **kwargs):
            return self.get_queryset().restore(*args, **kwargs)

    return QuerySetManager()


def MultiPassThroughManager(*classes):
    from model_utils.managers import PassThroughManager
    classes += (M2MPermanentManager, )
    name = "".join([cls.__name__ for cls in classes])
    return PassThroughManager.for_queryset_class(type(name, classes, {}))()
