from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import tempfile
import os
import logging
import re
from datetime import datetime

_logger = logging.getLogger(__name__)

try:
    import pytesseract
    from pdf2image import convert_from_bytes
    import cv2
    import numpy as np
except ImportError:
    _logger.error('Cannot import OCR libraries. Please install required dependencies.')

class Document(models.Model):
    _inherit = 'documents.document'

    ocr_processed = fields.Boolean(string='OCR Processed', default=False)
    ocr_text = fields.Text(string='OCR Text', readonly=True)
    extracted_data = fields.Text(string='Extracted Data', readonly=True)
    invoice_id = fields.Many2one('account.move', string='Related Invoice')
    
    def action_process_ocr(self):
        for document in self:
            if not document.attachment_id:
                raise UserError(_('No attachment found for this document.'))
            
            # Get OCR configuration
            config = self.env['invoice.ocr.config'].get_default_config()
            
            # Process the document with OCR
            file_data = base64.b64decode(document.attachment_id.datas)
            text = self._process_ocr(file_data, config)
            
            # Store the OCR text
            document.ocr_text = text
            
            # Extract structured data from OCR text
            extracted_data = self._extract_invoice_data(text)
            document.extracted_data = str(extracted_data)
            
            # Mark as processed
            document.ocr_processed = True
            
            # Create draft invoice if possible
            if extracted_data:
                self._create_draft_invoice(extracted_data)
    
    def _process_ocr(self, file_data, config):
        # Create a temporary file
        fd, temp_file_path = tempfile.mkstemp()
        try:
            with os.fdopen(fd, 'wb') as file:
                file.write(file_data)
            
            if config.use_external_service and config.service_url and config.api_key:
                # Use external OCR service
                return self._process_with_external_service(temp_file_path, config)
            else:
                # Use local Tesseract
                return self._process_with_tesseract(temp_file_path, config)
        finally:
            os.unlink(temp_file_path)
    
    def _process_with_tesseract(self, file_path, config):
        if config.tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = config.tesseract_path
        
        # Check if the file is PDF
        if file_path.lower().endswith('.pdf') or self.attachment_id.mimetype == 'application/pdf':
            pages = convert_from_bytes(open(file_path, 'rb').read())
            text = ""
            for page in pages:
                # Convert PIL Image to numpy array for OpenCV
                open_cv_image = np.array(page)
                # Convert RGB to BGR format for OpenCV
                open_cv_image = open_cv_image[:, :, ::-1].copy()
                
                # Preprocessing: Convert to grayscale and apply thresholding
                gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
                
                # OCR with Tesseract
                page_text = pytesseract.image_to_string(thresh, lang='tha+eng')
                text += page_text + "\n\n"
            
            return text
        else:
            # For image files
            image = cv2.imread(file_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
            
            # OCR with Tesseract
            text = pytesseract.image_to_string(thresh, lang='tha+eng')
            return text
    
    def _process_with_external_service(self, file_path, config):
        # Implementation for external OCR service
        # This is a placeholder - you'll need to implement the API call to your service
        _logger.info('Using external OCR service: %s', config.service_url)
        return "External OCR service implementation required"
    
    def _extract_invoice_data(self, text):
        # Extract key information from OCR text
        data = {}
        
        # Extract invoice number
        invoice_pattern = r'(?i)(?:invoice|ใบกำกับภาษี|ใบแจ้งหนี้|ใบเสร็จ).*?(?:no|number|เลขที่)[.:\s]*([\w\d/-]+)'
        invoice_match = re.search(invoice_pattern, text)
        if invoice_match:
            data['invoice_number'] = invoice_match.group(1).strip()
        
        # Extract date
        date_pattern = r'(?i)(?:date|invoice date|วันที่)[.:\s]*([\d]{1,2}[/\-\.][\d]{1,2}[/\-\.][\d]{2,4})'
        date_match = re.search(date_pattern, text)
        if date_match:
            date_str = date_match.group(1)
            # Handle different date formats
            try:
                # Try with different date formats
                for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y', '%d/%m/%y', '%d-%m-%y', '%d.%m.%y']:
                    try:
                        data['date'] = datetime.strptime(date_str, fmt).date()
                        break
                    except ValueError:
                        continue
            except Exception as e:
                _logger.error('Error parsing date: %s', e)
        
        # Extract amount
        amount_pattern = r'(?i)(?:total|amount|รวมเงิน|ยอดรวม)[.:\s]*([\d,]+\.?\d*)'
        amount_match = re.search(amount_pattern, text)
        if amount_match:
            try:
                amount_str = amount_match.group(1).replace(',', '')
                data['amount'] = float(amount_str)
            except Exception as e:
                _logger.error('Error parsing amount: %s', e)
        
        # Extract VAT
        vat_pattern = r'(?i)(?:vat|tax|ภาษีมูลค่าเพิ่ม)[.:\s]*([\d,]+\.?\d*)[%]?'
        vat_match = re.search(vat_pattern, text)
        if vat_match:
            try:
                vat_str = vat_match.group(1).replace(',', '')
                data['vat'] = float(vat_str)
            except Exception as e:
                _logger.error('Error parsing VAT: %s', e)
        
        # Extract vendor name
        vendor_pattern = r'(?i)(?:vendor|supplier|from|จาก|ผู้ขาย)[.:\s]*([^\n]*)'
        vendor_match = re.search(vendor_pattern, text)
        if vendor_match:
            data['vendor_name'] = vendor_match.group(1).strip()
        
        return data
    
    def _create_draft_invoice(self, data):
        if not data.get('invoice_number'):
            return False
        
        # Check if partner exists
        partner = False
        if data.get('vendor_name'):
            partner = self.env['res.partner'].search([
                ('name', 'ilike', data.get('vendor_name'))
            ], limit=1)
        
        if not partner:
            # Use default vendor
            partner = self.env.ref('base.main_partner', raise_if_not_found=False)
        
        # Create invoice
        invoice_vals = {
            'move_type': 'in_invoice',
            'partner_id': partner.id if partner else False,
            'ref': data.get('invoice_number', ''),
            'invoice_date': data.get('date', fields.Date.today()),
        }
        
        if data.get('amount'):
            # Add invoice line
            invoice_vals['invoice_line_ids'] = [(0, 0, {
                'name': 'Imported from OCR',
                'quantity': 1,
                'price_unit': data.get('amount', 0.0),
            })]
        
        invoice = self.env['account.move'].create(invoice_vals)
        self.invoice_id = invoice.id
        
        return invoice