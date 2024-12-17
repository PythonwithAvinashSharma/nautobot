from nautobot.apps.ui import NavMenuTab, NavMenuGroup, NavMenuItem, NavMenuAddButton

# Custom Dashboard navigation

menu_items = (
    NavMenuTab(
        name="DASHBOARD",  # Custom top-level tab name
        weight=50,  # Adjust weight to control its position in the navigation bar
        groups=(
            NavMenuGroup(
                name="DEVICE HEALTH",
                weight=10,
                items=(
                    NavMenuItem(
                        link="plugins:dashboard_plugin:dashboard",  # Replace with your view's URL name
                        name="Health Dashboard",
                        weight=10,
                        permissions=["plugins:dashboard_plugin.dashboard"],
                        buttons=(
                            NavMenuAddButton(
                                link="plugins:dashboard_plugin:add_dashboard",
                                permissions=["plugins:dashboard_plugin.add_dashboard"],
                            ),
                        ),
                    ),
                ),
            ),
        ),
    ),
)
