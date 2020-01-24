from .choices import IPAddressRoleChoices

# BGP ASN bounds
BGP_ASN_MIN = 1
BGP_ASN_MAX = 2**32 - 1


#
# VRFs
#

# Per RFC 4364 section 4.2, a route distinguisher may be encoded as one of the following:
#   * Type 0 (16-bit AS number : 32-bit integer)
#   * Type 1 (32-bit IPv4 address : 16-bit integer)
#   * Type 2 (32-bit AS number : 16-bit integer)
# 21 characters are sufficient to convey the longest possible string value (255.255.255.255:65535)
VRF_RD_MAX_LENGTH = 21


#
# Prefixes
#

PREFIX_LENGTH_MIN = 1
PREFIX_LENGTH_MAX = 127  # IPv6


#
# IPAddresses
#

IPADDRESS_MASK_LENGTH_MIN = 1
IPADDRESS_MASK_LENGTH_MAX = 128  # IPv6

IPADDRESS_ROLES_NONUNIQUE = (
    # IPAddress roles which are exempt from unique address enforcement
    IPAddressRoleChoices.ROLE_ANYCAST,
    IPAddressRoleChoices.ROLE_VIP,
    IPAddressRoleChoices.ROLE_VRRP,
    IPAddressRoleChoices.ROLE_HSRP,
    IPAddressRoleChoices.ROLE_GLBP,
    IPAddressRoleChoices.ROLE_CARP,
)


#
# VLANs
#

# 12-bit VLAN ID (values 0 and 4095 are reserved)
VLAN_VID_MIN = 1
VLAN_VID_MAX = 4094


#
# Services
#

# 16-bit port number
SERVICE_PORT_MIN = 1
SERVICE_PORT_MAX = 65535
