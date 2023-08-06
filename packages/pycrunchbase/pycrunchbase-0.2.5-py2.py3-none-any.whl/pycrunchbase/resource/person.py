import six

from .node import Node
from .utils import parse_date


@six.python_2_unicode_compatible
class Person(Node):
    """Represents a Person on CrunchBase
    API Docs: https://developer.crunchbase.com/docs
    """

    KNOWN_RELATIONSHIPS = [
        "degrees",
        "experience",
        "primary_location",
        "primary_affiliation",
        "investments",
        "advisor_at",
        "founded_companies",
        "primary_image",
        "websites",
        "news"
    ]

    KNOWN_PROPERTIES = [
        "role_investor",
        "last_name",
        "first_name",
        "permalink",
        "died_on_trust_code",
        "died_on_day",
        "died_on_month",
        "died_on_year",
        "died_on",
        "bio",
        "born_on_trust_code",
        "born_on_day",
        "born_on_month",
        "born_on_year",
        "born_on",
        "created_at",
        "updated_at",
        "location_uuid",
    ]

    def _coerce_values(self):
        """A delegate method to handle parsing all data and converting
        them into python values
        """
        # special cases to convert strings to pythonic value
        for attr in ['born_on', 'died_on']:
            if getattr(self, attr, None):
                setattr(self, attr, parse_date(getattr(self, attr)))

    def __str__(self):
        return u'{first} {last} ({permalink})'.format(
            first=self.first_name,
            last=self.last_name,
            permalink=self.permalink,
        )

    def __repr__(self):
        return self.__str__()
