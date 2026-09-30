from datetime import date

from lxml import etree

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

    def test_partner_form_shows_alternative_phones(self):
        arch = self.env["res.partner"].get_view(
            self.env.ref("base.view_partner_form").id, "form"
        )["arch"]
        form = etree.fromstring(arch)

        for field_name, placeholder in (
            ("phone_2", "Teléfono 2"),
            ("phone_3", "Teléfono 3"),
        ):
            fields = form.xpath(f"//field[@name='{field_name}']")
            self.assertEqual(len(fields), 1)
            self.assertEqual(fields[0].get("placeholder"), placeholder)
            self.assertEqual(fields[0].get("widget"), "phone")
            self.assertFalse(
                fields[0].getparent().xpath("field[@name='phone']"),
                f"{field_name} must not share the row of the main phone",
            )
