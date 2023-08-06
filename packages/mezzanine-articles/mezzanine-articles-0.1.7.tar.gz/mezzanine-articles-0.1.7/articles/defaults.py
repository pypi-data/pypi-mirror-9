from django.utils.translation import ugettext_lazy as _
from mezzanine.conf import register_setting


register_setting(
    name="TEMPLATE_ACCESSIBLE_SETTINGS",
    description="Sequence of setting names available within templates.",
    editable=False,
    default=(
        "CONTACT_COMPANY_NAME", "CONTACT_ADDRESS_1", "CONTACT_ADDRESS_2",
        "CONTACT_PHONE", "CONTACT_EMAIL", "CONTACT_CREATOR_NAME",
        "CONTACT_CREATOR_SITE", "CONTACT_FAX", "CONTACT_COMPANY_COPYRIGHTS",),
    append=True,
)

register_setting(
    name="CONTACT_COMPANY_NAME",
    label=_("Company name"),
    description=_("Company or site owner name (used in copyright for ex.)."),
    editable=True,
    default='',
    #translatable=True,
)
register_setting(
    name="CONTACT_COMPANY_COPYRIGHTS",
    label=_("Company copyrights"),
    description=_("Company or site legals information url."),
    editable=True,
    default='/legals/',
    #translatable=True,
)
register_setting(
    name="CONTACT_ADDRESS_1",
    label=_("Address 1"),
    description=_("First line of contact address."),
    editable=True,
    default='',
    #translatable=True,
)
register_setting(
    name="CONTACT_ADDRESS_2",
    label=_("Address 2"),
    description=_("Second line of contact address."),
    editable=True,
    default='',
    #translatable=True,
)
register_setting(
    name="CONTACT_PHONE",
    label=_("Phone"),
    description=_("Phone number(s)."),
    editable=True,
    default='',
    #translatable=True,
)
register_setting(
    name="CONTACT_FAX",
    label=_("Fax"),
    description=_("Fax number(s)."),
    editable=True,
    default='',
    #translatable=True,
)
register_setting(
    name="CONTACT_EMAIL",
    label=_("Email"),
    description=_("Email address."),
    editable=True,
    default='',
    #translatable=True,
)
register_setting(
    name="CONTACT_CREATOR_NAME",
    label=_("Creator name"),
    description=_("Creator company name"),
    editable=False,
    default='AIP',
    #translatable=True,
)
register_setting(
    name="CONTACT_CREATOR_SITE",
    label=_("Creator site"),
    description=_("Creator site address."),
    editable=False,
    default='http://www.aip.pl/',
    #translatable=True,
)
