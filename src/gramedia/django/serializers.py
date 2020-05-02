from rest_framework import serializers


class EntityHrefField(serializers.HyperlinkedRelatedField):
    """ Works the same as a hyperlinked related field, just nesting the response in a dict.
    """
    def to_representation(self, value):
        return {
            "title": str(value.name),
            "href": super(EntityHrefField, self).to_representation(value)
        }
