from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, new_test_user, tagged


@tagged("post_install", "-at_install")
class TestStockTransferEmployee(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.company.id)], limit=1
        )
        cls.internal_type = cls.warehouse.int_type_id
        cls.outgoing_type = cls.warehouse.out_type_id
        cls.stock_location = cls.warehouse.lot_stock_id
        cls.dest_location = cls.env["stock.location"].create(
            {
                "name": "Transfer Employee Shelf",
                "usage": "internal",
                "location_id": cls.stock_location.id,
            }
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Transfer Employee Product", "is_storable": True}
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.stock_location, 10
        )
        cls.employee = cls.env["hr.employee"].create(
            {"name": "Transfer Hairdresser", "company_id": cls.company.id}
        )
        cls.employee_contact = cls.employee.work_contact_id
        cls.customer = cls.env["res.partner"].create({"name": "Transfer Customer"})
        cls.stock_user = new_test_user(
            cls.env, login="transfer_stock_user", groups="stock.group_stock_user"
        )

    def _create_picking(self, partner=None, picking_type=None):
        picking_type = picking_type or self.internal_type
        location_dest = (
            self.dest_location
            if picking_type == self.internal_type
            else self.env.ref("stock.stock_location_customers")
        )
        return self.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "partner_id": partner.id if partner else False,
                "location_id": self.stock_location.id,
                "location_dest_id": location_dest.id,
                "move_ids": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "location_id": self.stock_location.id,
                            "location_dest_id": location_dest.id,
                        }
                    )
                ],
            }
        )

    def test_employee_contact_flag(self):
        self.assertTrue(self.employee_contact.is_employee_contact)
        self.assertFalse(self.customer.is_employee_contact)

    def test_search_employee_contacts_without_hr_rights(self):
        partners = self.env["res.partner"].with_user(self.stock_user)
        employee_contacts = partners.search([("is_employee_contact", "=", True)])
        other_contacts = partners.search([("is_employee_contact", "=", False)])
        self.assertIn(self.employee_contact, employee_contacts)
        self.assertNotIn(self.customer, employee_contacts)
        self.assertIn(self.customer, other_contacts)
        self.assertNotIn(self.employee_contact, other_contacts)

    def test_archived_employee_is_not_employee_contact(self):
        self.employee.active = False
        self.employee_contact.invalidate_recordset(["is_employee_contact"])
        self.assertFalse(self.employee_contact.is_employee_contact)
        picking = self._create_picking(self.employee_contact)
        with self.assertRaises(ValidationError):
            picking.action_confirm()

    def test_confirm_internal_transfer_with_employee(self):
        picking = self._create_picking(self.employee_contact)
        picking.with_user(self.stock_user).action_confirm()
        self.assertEqual(picking.state, "assigned")

    def test_confirm_internal_transfer_without_contact(self):
        picking = self._create_picking()
        with self.assertRaisesRegex(ValidationError, picking.name):
            picking.action_confirm()
        self.assertEqual(picking.state, "draft")

    def test_confirm_internal_transfer_with_non_employee(self):
        picking = self._create_picking(self.customer)
        with self.assertRaises(ValidationError):
            picking.with_user(self.stock_user).action_confirm()
        self.assertEqual(picking.state, "draft")

    def test_validate_draft_internal_transfer(self):
        rejected = self._create_picking(self.customer)
        with self.assertRaises(ValidationError):
            rejected.button_validate()
        self.assertEqual(rejected.state, "draft")

        accepted = self._create_picking(self.employee_contact)
        accepted.button_validate()
        self.assertEqual(accepted.state, "done")

    def test_contact_changed_after_confirmation_is_rejected(self):
        picking = self._create_picking(self.employee_contact)
        picking.action_confirm()
        picking.partner_id = self.customer
        with self.assertRaises(ValidationError):
            picking.button_validate()
        self.assertNotEqual(picking.state, "done")

    def test_employee_of_other_company_is_rejected(self):
        other_company = self.env["res.company"].create({"name": "Other Salon"})
        other_employee = self.env["hr.employee"].create(
            {"name": "Other Hairdresser", "company_id": other_company.id}
        )
        picking = self._create_picking(other_employee.work_contact_id)
        with self.assertRaises(ValidationError):
            picking.action_confirm()

    def test_error_lists_every_invalid_transfer(self):
        pickings = self._create_picking(self.customer) | self._create_picking()
        with self.assertRaises(ValidationError) as error:
            pickings.action_confirm()
        for picking in pickings:
            self.assertIn(picking.name, str(error.exception))

    def test_other_operation_types_are_not_restricted(self):
        picking = self._create_picking(self.customer, self.outgoing_type)
        picking.action_confirm()
        self.assertEqual(picking.state, "assigned")

    def test_form_filters_contacts_for_internal_transfers(self):
        arch = self.env["stock.picking"].get_view(
            self.env.ref("stock.view_picking_form").id, "form"
        )["arch"]
        self.assertIn("is_employee_contact", arch)
        self.assertIn("picking_type_code == 'internal'", arch)
