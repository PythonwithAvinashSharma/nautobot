from nautobot.apps.ui import NavMenuTab, NavMenuGroup, NavMenuItem, NavMenuAddButton

# Custom Dashboard navigation

menu_items = (
    NavMenuTab(
        name="NW Catalog",  # Custom top-level tab name
        weight=60,  # Adjust weight to control its position in the navigation bar
        groups=(
            NavMenuGroup(
                name="SITE ONBOARDING",
                weight=10,
                items=(
                    NavMenuItem(
                        link="plugins:naas:site-onboarding",  # Replace with your view's URL name
                        name="SITES ONBOARDING",
                        weight=10,
                        permissions=["plugins:naas.site-onboarding"],
                    ),
                ),
            ),
            NavMenuGroup(
                name="VLAN CONFIGURATION",
                weight=20,
                items=(
                    NavMenuItem(
                        link="plugins:naas:vlan-config",  # Replace with your view's URL name
                        name="VLAN CONFIGURATION",
                        weight=10,
                        permissions=["plugins:naas:vlan-config"],
                    ),
                ),
            ),
            NavMenuGroup(
                name="Switch Configuration",
                weight=30,
                items=(
                    NavMenuItem(
                        link="plugins:naas:switches",  # Replace with your view's URL name
                        name="Catalog",
                        weight=10,
                        permissions=["plugins:naas:switches"],
                    ),
                ),
            ),
        ),
    ),
)
