# Copyright 2026 Xtendoo - Xtendoo Corporation
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from datetime import datetime, timedelta

from odoo import fields
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestDailyClose(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.company_data["company"]
        cls.journal_cash = cls.company_data["default_journal_cash"]
        cls.journal_bank = cls.company_data["default_journal_bank"]
        cls.pm_cash = (
            cls.env["pos.payment.method"]
            .sudo()
            .create(
                {
                    "name": "Efectivo",
                    "journal_id": cls.journal_cash.id,
                    "company_id": cls.company.id,
                }
            )
        )
        cls.pm_bank = (
            cls.env["pos.payment.method"]
            .sudo()
            .create(
                {
                    "name": "Tarjeta",
                    "journal_id": cls.journal_bank.id,
                    "company_id": cls.company.id,
                }
            )
        )
        config = (
            cls.env["pos.config"]
            .sudo()
            .create({"name": "TPV Test", "company_id": cls.company.id})
        )
        cls.session = (
            cls.env["pos.session"]
            .sudo()
            .create(
                {
                    "config_id": config.id,
                    "user_id": cls.env.user.id,
                    "state": "opened",
                }
            )
        )
        cls.product_prosthesis = cls.env["product.product"].create(
            {
                "name": "Prótesis capilar",
                "list_price": 1000.0,
                "taxes_id": [(5, 0, 0)],
            }
        )
        cls.today = fields.Date.today()
        cls.yesterday = cls.today - timedelta(days=1)

    def _create_pos_order(self, payments, date_order=None):
        """Crea un pedido TPV pagado con los cobros indicados.

        :param payments: lista de tuplas (pos.payment.method, importe, is_change)
        """
        total = sum(amount for _pm, amount, is_change in payments if not is_change)
        order = (
            self.env["pos.order"]
            .sudo()
            .create(
                {
                    "name": "TPV/TEST",
                    "session_id": self.session.id,
                    "company_id": self.company.id,
                    "amount_tax": 0.0,
                    "amount_total": total,
                    "amount_paid": total,
                    "amount_return": 0.0,
                    "date_order": date_order or fields.Datetime.now(),
                    "state": "paid",
                }
            )
        )
        for payment_method, amount, is_change in payments:
            self.env["pos.payment"].sudo().create(
                {
                    "pos_order_id": order.id,
                    "amount": amount,
                    "payment_method_id": payment_method.id,
                    "is_change": is_change,
                }
            )
        return order

    def _create_sale(self, date_order=None):
        sale = (
            self.env["sale.order"]
            .sudo()
            .create(
                {
                    "partner_id": self.partner_a.id,
                    "company_id": self.company.id,
                    "date_order": date_order or fields.Datetime.now(),
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "product_id": self.product_prosthesis.id,
                                "product_uom_qty": 1,
                                "price_unit": 1000.0,
                            },
                        )
                    ],
                }
            )
        )
        sale.action_confirm()
        if date_order:
            # action_confirm sobrescribe date_order con la fecha actual.
            sale.date_order = date_order
        return sale

    def _advance_and_collect(self, sale, percentage, journal):
        wizard = (
            self.env["sale.advance.payment.inv"]
            .sudo()
            .with_context(active_ids=sale.ids)
            .create({"advance_payment_method": "percentage", "amount": percentage})
        )
        wizard.create_invoices()
        invoice = sale.invoice_ids.filtered(
            lambda move: move.move_type == "out_invoice"
        )[:1]
        invoice.action_post()
        self._register_payment(invoice, journal)
        return invoice

    def _register_payment(self, invoice, journal):
        register = (
            self.env["account.payment.register"]
            .sudo()
            .with_context(active_model="account.move", active_ids=invoice.ids)
            .create({"journal_id": journal.id, "amount": invoice.amount_residual})
        )
        register._create_payments()

    def _summary(self, date=None, date_to=None):
        date_from = date or self.today
        return self.env["hairsalon.daily.close"].get_summary(
            date_from, date_to or date_from, self.company
        )

    def _create_invoice_without_sale(self, amount):
        journal = self.env["account.journal"].search(
            [("type", "=", "sale"), ("company_id", "=", self.company.id)], limit=1
        )
        invoice = (
            self.env["account.move"]
            .sudo()
            .create(
                {
                    "move_type": "out_invoice",
                    "partner_id": self.partner_a.id,
                    "company_id": self.company.id,
                    "journal_id": journal.id,
                    "invoice_line_ids": [
                        (
                            0,
                            0,
                            {"name": "Servicio", "quantity": 1, "price_unit": amount},
                        )
                    ],
                }
            )
        )
        invoice.action_post()
        return invoice

    def _payments(self, domain=None):
        return (
            self.env["hairsalon.daily.close.payment"]
            .sudo()
            .search([("company_id", "=", self.company.id), *(domain or [])])
        )

    def test_pos_sale_paid_in_full(self):
        order = self._create_pos_order([(self.pm_cash, 100.0, False)])
        summary = self._summary()
        self.assertEqual(summary["total_sold"], 100.0)
        self.assertEqual(summary["total_collected"], 100.0)
        self.assertEqual(summary["pending_collection"], 0.0)
        self.assertEqual(summary["expected_cash"], 100.0)
        payment = self._payments([("pos_order_id", "=", order.id)])
        self.assertEqual(len(payment), 1)
        self.assertEqual(payment.origin, "pos")
        self.assertTrue(payment.is_cash)

    def test_pos_change_subtracts_expected_cash(self):
        self._create_pos_order(
            [
                (self.pm_cash, 50.0, False),
                (self.pm_cash, 5.0, True),
            ]
        )
        self.assertEqual(self._summary()["expected_cash"], 45.0)

    def test_sales_partial_advance_prosthesis(self):
        sale = self._create_sale()
        self._advance_and_collect(sale, 50.0, self.journal_cash)
        summary = self._summary()
        self.assertEqual(summary["total_sold"], 1000.0)
        self.assertEqual(summary["total_collected"], 500.0)
        self.assertEqual(summary["pending_collection"], 500.0)
        self.assertEqual(summary["expected_cash"], 500.0)
        payment = self._payments([("sale_order_id", "=", sale.id)])
        self.assertEqual(sum(payment.mapped("amount")), 500.0)
        self.assertEqual(set(payment.mapped("origin")), {"sale"})

    def test_collection_today_for_yesterday_sale(self):
        yesterday = datetime.combine(self.yesterday, datetime.min.time())
        sale = self._create_sale(date_order=yesterday)
        self._advance_and_collect(sale, 50.0, self.journal_bank)
        today_summary = self._summary()
        self.assertEqual(today_summary["total_sold"], 0.0)
        self.assertEqual(today_summary["total_collected"], 500.0)
        self.assertEqual(today_summary["expected_cash"], 0.0)
        yesterday_summary = self._summary(self.yesterday)
        self.assertEqual(yesterday_summary["total_sold"], 1000.0)
        self.assertEqual(yesterday_summary["total_collected"], 0.0)
        # El pendiente incluye los cobros posteriores de las ventas del día.
        self.assertEqual(yesterday_summary["pending_collection"], 500.0)

    def test_mixed_payment_methods_pos(self):
        self._create_pos_order(
            [
                (self.pm_cash, 60.0, False),
                (self.pm_bank, 40.0, False),
            ]
        )
        summary = self._summary()
        self.assertEqual(summary["total_sold"], 100.0)
        self.assertEqual(summary["total_collected"], 100.0)
        self.assertEqual(summary["expected_cash"], 60.0)
        methods = {line["method"]: line["amount"] for line in summary["payments"]}
        self.assertEqual(methods[self.pm_cash.name], 60.0)
        self.assertEqual(methods[self.pm_bank.name], 40.0)

    def test_pos_payment_produces_single_row(self):
        order = self._create_pos_order([(self.pm_bank, 80.0, False)])
        payments = self._payments([("pos_order_id", "=", order.id)])
        self.assertEqual(len(payments), 1)

    def test_invoice_payment_without_sale_order_is_collected(self):
        invoice = self._create_invoice_without_sale(300.0)
        self._register_payment(invoice, self.journal_cash)
        summary = self._summary()
        self.assertEqual(summary["total_sold"], 0.0)
        self.assertEqual(summary["total_collected"], 300.0)
        self.assertEqual(summary["expected_cash"], 300.0)
        payment = self._payments(
            [("sale_order_id", "=", False), ("origin", "=", "sale")]
        )
        self.assertEqual(sum(payment.mapped("amount")), 300.0)

    def test_date_range_includes_collection_in_period(self):
        yesterday = datetime.combine(self.yesterday, datetime.min.time())
        sale = self._create_sale(date_order=yesterday)
        self._advance_and_collect(sale, 50.0, self.journal_cash)
        summary = self._summary(self.yesterday, self.today)
        self.assertEqual(summary["total_sold"], 1000.0)
        self.assertEqual(summary["total_collected"], 500.0)
        self.assertEqual(summary["pending_collection"], 500.0)
        self.assertEqual(summary["expected_cash"], 500.0)

    def test_summary_without_movements_is_zero(self):
        summary = self._summary(self.yesterday - timedelta(days=30))
        self.assertEqual(summary["total_sold"], 0.0)
        self.assertEqual(summary["total_collected"], 0.0)
        self.assertEqual(summary["expected_cash"], 0.0)
        self.assertEqual(summary["sales"][0]["amount"], 0.0)
