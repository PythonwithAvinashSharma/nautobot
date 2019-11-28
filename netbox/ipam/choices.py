from utilities.choices import ChoiceSet


#
# Prefixes
#

class PrefixStatusChoices(ChoiceSet):

    STATUS_CONTAINER = 'container'
    STATUS_ACTIVE = 'active'
    STATUS_RESERVED = 'reserved'
    STATUS_DEPRECATED = 'deprecated'

    CHOICES = (
        (STATUS_CONTAINER, 'Container'),
        (STATUS_ACTIVE, 'Active'),
        (STATUS_RESERVED, 'Reserved'),
        (STATUS_DEPRECATED, 'Deprecated'),
    )

    LEGACY_MAP = {
        STATUS_CONTAINER: 0,
        STATUS_ACTIVE: 1,
        STATUS_RESERVED: 2,
        STATUS_DEPRECATED: 3,
    }


#
# IPAddresses
#

class IPAddressStatusChoices(ChoiceSet):

    STATUS_ACTIVE = 'active'
    STATUS_RESERVED = 'reserved'
    STATUS_DEPRECATED = 'deprecated'
    STATUS_DHCP = 'dhcp'

    CHOICES = (
        (STATUS_ACTIVE, 'Active'),
        (STATUS_RESERVED, 'Reserved'),
        (STATUS_DEPRECATED, 'Deprecated'),
        (STATUS_DHCP, 'DHCP'),
    )

    LEGACY_MAP = {
        STATUS_ACTIVE: 1,
        STATUS_RESERVED: 2,
        STATUS_DEPRECATED: 3,
        STATUS_DHCP: 5,
    }
