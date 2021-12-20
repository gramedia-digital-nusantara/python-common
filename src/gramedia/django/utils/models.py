from django.db import models
from django.db.models import SlugField, Model
from django.utils.text import slugify


def generate_slug(model_class: Model, base_text: str, tries=0) -> str:
    """ Create a unique slug for the given model_class.

    .. warning::

        Makes the slightly naive assumption that your slug field will be called 'slug'

    :param model_class: A django model class (NOT the instance)
    :param base_text: Some text to use as a base for the slug, such as the 'name'
    :param tries: Previous attempts to geenrate the slug
    :return: A unique slug for an item from the database.
    """
    candidate_slug = f'{slugify(base_text)}-{tries}' if tries else slugify(base_text)
    if model_class.objects.filter(slug=candidate_slug).exists():
        return generate_slug(model_class, base_text, tries + 1)
    return candidate_slug


class MonoLangSlugField(SlugField):
    """ Field that automatically generates a slug from a CharField before saving.
    """

    def __init__(self, from_field='name', *args, **kwargs):
        if not 'unique' in kwargs:
            kwargs['unique'] = True
        if not 'max_length' in kwargs:
            kwargs['max_length'] = 150
        super(MonoLangSlugField, self).__init__(*args, **kwargs)
        self.from_field = from_field

    def pre_save(self, model_instance: any, add: bool):
        if not getattr(model_instance, self.attname):
            source = getattr(model_instance, self.from_field)
            setattr(
                model_instance,
                self.attname,
                generate_slug(model_instance.__class__, source)
            )
        return super(MonoLangSlugField, self).pre_save(model_instance, add)


class TimestampedModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseModel(TimestampedModel):
    """ Common model for most of our standard use-cases.  Includes a name, slug, and is_active field.
    """
    name = models.CharField(max_length=70)
    slug = MonoLangSlugField()

    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name
