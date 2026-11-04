from lxml import etree

from odoo import Command
from odoo.tests import tagged
from odoo.tests.common import TransactionCase, new_test_user

from ..hooks import post_init_hook

GROUP_XMLID = "hairsalon_hide_cost_price.group_show_cost_price"
HIDDEN_VALUES = ("1", "True", "true")


@tagged("post_install", "-at_install")
class TestHideCostPrice(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = cls.env.ref(GROUP_XMLID)
        base_groups = (
            "base.group_user,base.group_partner_manager,"
            "point_of_sale.group_pos_user,stock.group_stock_manager"
        )
        cls.restricted_user = new_test_user(
            cls.env, login="hide_cost_restricted", groups=base_groups
        )
        cls.cost_user = new_test_user(
            cls.env,
            login="hide_cost_allowed",
            groups=f"{base_groups},{GROUP_XMLID}",
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Champú coste", "standard_price": 7.5, "list_price": 12.0}
        )

    def _arch(self, user, model, view_xmlid, view_type):
        view = self.env.ref(view_xmlid)
        arch = self.env[model].with_user(user).get_view(view.id, view_type)["arch"]
        return etree.fromstring(arch)

    @staticmethod
    def _is_shown(node):
        hiding_attrs = ("invisible", "column_invisible")
        return not any(node.get(attr) in HIDDEN_VALUES for attr in hiding_attrs)

    def _shown_fields(self, root, xpath="//field"):
        return {node.get("name") for node in root.xpath(xpath) if self._is_shown(node)}

    def _assert_hidden_only_without_group(
        self, model, view_xmlid, view_type, names, xpath="//field"
    ):
        restricted = self._shown_fields(
            self._arch(self.restricted_user, model, view_xmlid, view_type), xpath
        )
        allowed = self._shown_fields(
            self._arch(self.cost_user, model, view_xmlid, view_type), xpath
        )
        for name in names:
            with self.subTest(view=view_xmlid, field=name):
                self.assertNotIn(name, restricted)
                self.assertIn(name, allowed)

    def test_group_definition(self):
        self.assertIn(self.group, self.env.ref("base.group_system").implied_ids)
        self.assertIn(self.group, self.env.ref("base.user_admin").all_group_ids)
        self.assertEqual(
            self.group.privilege_id.category_id,
            self.env.ref("base.module_category_sales"),
        )
        self.assertNotIn(self.group, self.restricted_user.all_group_ids)

    def test_product_views(self):
        cases = (
            ("product.template", "product.product_template_form_view", "form"),
            ("product.template", "product.product_template_only_form_view", "form"),
            ("product.template", "product.product_template_tree_view", "list"),
            ("product.product", "product.product_normal_form_view", "form"),
            ("product.product", "product.product_variant_easy_edit_view", "form"),
            ("product.product", "product.product_product_tree_view", "list"),
        )
        for model, view_xmlid, view_type in cases:
            self._assert_hidden_only_without_group(
                model, view_xmlid, view_type, ["standard_price"]
            )

    def test_product_form_cost_label_hidden(self):
        for user, expected in ((self.restricted_user, 0), (self.cost_user, 1)):
            root = self._arch(
                user, "product.template", "product.product_template_form_view", "form"
            )
            self.assertEqual(
                len(root.xpath("//label[@for='standard_price']")), expected
            )
            self.assertEqual(
                len(root.xpath("//div[@name='standard_price_uom']")), expected
            )

    def test_product_kanban_and_search_never_show_cost(self):
        for model, view_xmlid, view_type in (
            ("product.template", "product.product_template_kanban_view", "kanban"),
            ("product.product", "product.product_kanban_view", "kanban"),
            ("product.template", "product.product_template_search_view", "search"),
        ):
            root = self._arch(self.restricted_user, model, view_xmlid, view_type)
            self.assertNotIn("standard_price", self._shown_fields(root), view_xmlid)

    def test_stock_valuation_views(self):
        cases = (
            (
                "product.product",
                "stock.product_product_stock_tree",
                "list",
                ["avg_cost", "total_value"],
            ),
            (
                "product.product",
                "stock.view_stock_product_tree",
                "list",
                ["avg_cost", "total_value", "standard_price"],
            ),
            ("stock.quant", "stock.view_stock_quant_tree", "list", ["value"]),
            ("stock.quant", "stock.view_stock_quant_tree_editable", "list", ["value"]),
            (
                "stock.move",
                "stock.view_move_tree",
                "list",
                ["value", "remaining_value"],
            ),
            (
                "stock.move",
                "stock_account.stock_move_view_list_valuation",
                "list",
                ["value", "standard_price"],
            ),
            (
                "stock.lot",
                "stock.view_production_lot_form",
                "form",
                ["total_value", "avg_cost", "standard_price"],
            ),
        )
        for model, view_xmlid, view_type, names in cases:
            self._assert_hidden_only_without_group(model, view_xmlid, view_type, names)

    def test_pos_order_form(self):
        self._assert_hidden_only_without_group(
            "pos.order",
            "point_of_sale.view_pos_pos_form",
            "form",
            ["total_cost", "margin", "margin_percent"],
            xpath="//field[@name='lines']/list/field",
        )
        self._assert_hidden_only_without_group(
            "pos.order",
            "point_of_sale.view_pos_pos_form",
            "form",
            ["margin", "margin_percent"],
            xpath="//page[@name='products']//field",
        )

    def _invisible_measures(self, user, model, view_xmlid, view_type):
        root = self._arch(user, model, view_xmlid, view_type)
        return {
            node.get("name")
            for node in root.xpath("//field")
            if not self._is_shown(node)
        }

    def test_analysis_measures(self):
        cases = (
            ("pos.order", "point_of_sale.view_pos_order_pivot", "pivot", ["margin"]),
            (
                "pos.order",
                "hairsalon_hide_cost_price.view_pos_order_graph",
                "graph",
                ["margin", "margin_percent"],
            ),
            (
                "report.pos.order",
                "point_of_sale.view_report_pos_order_pivot",
                "pivot",
                ["margin"],
            ),
            (
                "report.pos.order",
                "point_of_sale.view_report_pos_order_graph",
                "graph",
                ["margin"],
            ),
            (
                "stock.move",
                "stock.view_move_pivot",
                "pivot",
                ["value", "value_manual", "remaining_value"],
            ),
            (
                "stock.move",
                "stock.view_move_graph",
                "graph",
                ["value", "value_manual", "remaining_value"],
            ),
        )
        for model, view_xmlid, view_type, names in cases:
            restricted = self._invisible_measures(
                self.restricted_user, model, view_xmlid, view_type
            )
            allowed = self._invisible_measures(
                self.cost_user, model, view_xmlid, view_type
            )
            for name in names:
                with self.subTest(view=view_xmlid, field=name):
                    self.assertIn(name, restricted)
                    self.assertNotIn(name, allowed)

    def test_pos_order_graph_is_default_graph(self):
        view = (
            self.env["pos.order"].with_user(self.cost_user).get_view(view_type="graph")
        )
        graph_view = self.env.ref("hairsalon_hide_cost_price.view_pos_order_graph")
        self.assertEqual(view["id"], graph_view.id)
        root = etree.fromstring(view["arch"])
        self.assertEqual(self._shown_fields(root), {"name"})

    def test_cost_field_still_readable_for_pos(self):
        """The POS front-end loads standard_price: it must not be field-restricted."""
        field_groups = self.env["product.product"]._fields["standard_price"].groups
        self.assertNotIn("group_show_cost_price", field_groups or "")
        product = self.product.with_user(self.restricted_user)
        self.assertEqual(product.read(["standard_price"])[0]["standard_price"], 7.5)

    def test_post_init_hook(self):
        salon_user = new_test_user(
            self.env, login="peluqueria", groups="base.group_user"
        )
        archived_user = new_test_user(
            self.env, login="hide_cost_archived", groups="base.group_user"
        )
        archived_user.active = False
        portal_user = new_test_user(
            self.env, login="hide_cost_portal", groups="base.group_portal"
        )
        post_init_hook(self.env)
        post_init_hook(self.env)
        self.assertIn(self.group, self.restricted_user.group_ids)
        self.assertIn(self.group, archived_user.group_ids)
        self.assertNotIn(self.group, salon_user.all_group_ids)
        self.assertNotIn(self.group, portal_user.all_group_ids)
        self.assertEqual(self.restricted_user.group_ids.ids.count(self.group.id), 1)

    def test_group_can_be_removed_from_user(self):
        self.cost_user.write({"group_ids": [Command.unlink(self.group.id)]})
        root = self._arch(
            self.cost_user,
            "product.product",
            "product.product_product_tree_view",
            "list",
        )
        self.assertNotIn("standard_price", self._shown_fields(root))
