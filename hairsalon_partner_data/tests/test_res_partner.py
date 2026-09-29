from datetime import date

from odoo.tests.common import TransactionCase


class TestResPartner(TransactionCase):

    def test_customer_contact_data(self):
        partner = self.env["res.partner"].create(
            {
                "name": "Cliente Hairsalon",
                "phone_2": "+34 600 000 001",
                "phone_3": "+34 600 000 002",
                "birthdate_date": date(1990, 5, 17),
            }
        )

        self.assertEqual(partner.phone_2, "+34 600 000 001")
        self.assertEqual(partner.phone_3, "+34 600 000 002")
        self.assertEqual(partner.birthdate_date, date(1990, 5, 17))
