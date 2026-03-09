from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

class TestHairsalonBrands(TransactionCase):

    def setUp(self):
        super(TestHairsalonBrands, self).setUp()
        self.Brand = self.env['hairsalon.brand']
        self.BrandLine = self.env['hairsalon.brand.line']
        self.ProductTemplate = self.env['product.template']

        # Create a brand
        self.brand_loreal = self.Brand.create({
            'name': "L'Oreal",
        })

        # Create brand lines
        self.line_shampoo = self.BrandLine.create({
            'name': 'Shampoo',
            'brand_id': self.brand_loreal.id,
        })
        self.line_body_care = self.BrandLine.create({
            'name': 'Body Care',
            'brand_id': self.brand_loreal.id,
        })

    def test_01_brand_creation(self):
        """Test brand and brand line creation"""
        self.assertEqual(len(self.brand_loreal.line_ids), 2)
        self.assertIn(self.line_shampoo, self.brand_loreal.line_ids)
        self.assertEqual(self.line_shampoo.brand_id, self.brand_loreal)

    def test_02_product_brand_assignment(self):
        """Test assigning a brand and a line to a product"""
        product = self.ProductTemplate.create({
            'name': 'Loreal Super Shampoo',
            'brand_id': self.brand_loreal.id,
            'brand_line_id': self.line_shampoo.id,
        })
        self.assertEqual(product.brand_id, self.brand_loreal)
        self.assertEqual(product.brand_line_id, self.line_shampoo)

    def test_03_brand_deletion_cascade(self):
        """Test that deleting a brand deletes its lines"""
        line_ids = self.brand_loreal.line_ids.ids
        
        # Delete the brand
        self.brand_loreal.unlink()
        
        # Check that lines are also deleted because of ondelete='cascade'
        lines = self.BrandLine.search([('id', 'in', line_ids)])
        self.assertEqual(len(lines), 0)
