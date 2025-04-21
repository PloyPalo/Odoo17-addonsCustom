from odoo import models, fields, api

class OcrConfiguration(models.Model):
    _name = 'invoice.ocr.config'
    _description = 'OCR Configuration'

    name = fields.Char(string='Name', required=True)
    api_key = fields.Char(string='API Key', help='API Key for OCR service')
    use_external_service = fields.Boolean(string='Use External OCR Service', default=False)
    service_url = fields.Char(string='Service URL', help='URL for external OCR service')
    tesseract_path = fields.Char(string='Tesseract Path', help='Path to Tesseract executable')
    active = fields.Boolean(default=True)
    
    @api.model
    def get_default_config(self):
        config = self.search([('active', '=', True)], limit=1)
        if not config:
            config = self.create({
                'name': 'Default Configuration',
                'use_external_service': False,
                'tesseract_path': '/usr/bin/tesseract',
            })
        return config