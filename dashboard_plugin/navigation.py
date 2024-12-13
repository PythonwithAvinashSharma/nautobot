# # dashboard_plugin/navigation.py
# from nautobot.core.apps import NavMenuItem, NavMenuGroup, NavMenuTab

# menu_items = (
#     NavMenuTab(
#         name="Health Dashboard",
#         weight=100,  # Adjust weight to control position in the UI
#         groups=(
#             NavMenuGroup(
#                 name="Device Dashboard",
#                 weight=100,  # Position of the group
#                 items=(
#                     NavMenuItem(
#                         link="dashboard_plugin:dashboard",  # Reference to the view
#                         name="Dashboard",
#                         weight=100,  # Position of the item
#                         permissions=[
#                             "dashboard_plugin.view_dashboard",
#                         ],
#                     ),
#                 ),
#             ),
#         ),
#     ),
# )

"""App additions to the Nautobot navigation menu."""

from nautobot.apps.ui import NavMenuGroup, NavMenuItem, NavMenuTab

from dashboard_plugin.integrations.utils import each_enabled_integration_module

items = [
    NavMenuItem(
        link="plugins:dashboard_plugin:dashboard",
        name="Dashboard",
        permissions=["dashboard_plugin.view_dashboard"],
    ),
    # NavMenuItem(
    #     link="plugins:dashboard_plugin:sync_list",
    #     name="History",
    #     permissions=["dashboard_plugin.view_sync"],
    # ),
    # NavMenuItem(
    #     link="plugins:dashboard_plugin:synclogentry_list",
    #     name="Logs",
    #     permissions=["dashboard_plugin.view_synclogentry"],
    #),
]


def _add_integrations():
    for module in each_enabled_integration_module("navigation"):
        items.extend(module.nav_items)


_add_integrations()


menu_items = (
    NavMenuTab(
        name="ORGANIZATION",
        weight=100,
        groups=(
            NavMenuGroup(
                name="Dashboard",
                weight=150,
                items=(
                    NavMenuItem(
                        link="dashboard_plugin:location_list",
                        name="Dashboard",
                        weight=100,
                        permissions=[
                            "dashboard_plugin.view_location",
                        ],
                        buttons=(
                            NavMenuAddButton(
                                link="dashboard_plugin:location_add",
                                permissions=[
                                    "dashboard_plugin.add_location",
                                ],
                            ),
                        ),
                    ),
                ),
            ),
        ),
    ),
)