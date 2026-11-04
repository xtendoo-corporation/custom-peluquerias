from odoo import Command

EXCLUDED_LOGINS = ("peluqueria",)


def post_init_hook(env):
    """Keep the current behaviour: existing internal users still see costs."""
    group = env.ref("hairsalon_hide_cost_price.group_show_cost_price")
    users = (
        env["res.users"]
        .with_context(active_test=False)
        .search([("share", "=", False), ("login", "not in", EXCLUDED_LOGINS)])
    )
    users.filtered(lambda user: group not in user.group_ids).write(
        {"group_ids": [Command.link(group.id)]}
    )
