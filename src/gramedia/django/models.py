from django.db.models import Model
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
        return generate_slug(model_class, base_text, tries+1)
    return candidate_slug
