from odoo import api, fields, models, _
import base64
import csv
import io
import os.path
import logging

_logger = logging.getLogger(__name__)

ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif']

class ProductImageImportWizard(models.TransientModel):
    _name = 'product.image.import.wizard'
    _description = 'Import Product Images'

    csv_file = fields.Binary('CSV File', required=True)
    csv_filename = fields.Char('CSV Filename')
    image_directory = fields.Char('Image Directory', required=True,
                                    help='Specify the directory where the images are located, e.g., D:\\PIC\\')
    column_id = fields.Char('ID Column Name', default='id', required=True)
    column_image_path = fields.Char('Image Path Column Name', default='product_path_pic', required=True)
    image_field = fields.Selection([
        ('image_1920', 'Main Image'),
        # You can add more image fields here if needed
    ], string='Image Field', default='image_1920', required=True,
       help='Select the product image field to update.')

    import_log = fields.Text('Import Log', readonly=True)
    state = fields.Selection([
        ('choose', 'Choose File'),
        ('result', 'Result'),
    ], default='choose')

    image_directory_accessible = fields.Boolean('Image Directory Accessible', compute='_compute_image_directory_accessible', store=True)

    @api.depends('image_directory')
    def _compute_image_directory_accessible(self):
        for wizard in self:
            try:
                if wizard.image_directory:
                    is_accessible = os.path.isdir(wizard.image_directory) and os.access(wizard.image_directory, os.R_OK)
                    wizard.image_directory_accessible = is_accessible
                else:
                    wizard.image_directory_accessible = False
            except Exception:
                wizard.image_directory_accessible = False

    def action_import(self):
        self.ensure_one()

        log_messages = []
        success_count = 0
        error_count = 0
        skip_count = 0

        try:
            # Read the CSV file
            csv_data = base64.b64decode(self.csv_file)
            csv_file = io.StringIO(csv_data.decode('utf-8'))
            csv_reader = csv.DictReader(csv_file)

            for row in csv_reader:
                product_id = row.get(self.column_id, '')
                image_path = row.get(self.column_image_path, '')

                # Skip if no image path is provided
                if not image_path:
                    log_messages.append(f"Skipped: No image path found for product {product_id}")
                    skip_count += 1
                    continue

                # If an image directory is specified and the path is not absolute
                full_path = image_path
                if self.image_directory and not os.path.isabs(image_path):
                    full_path = os.path.join(self.image_directory, image_path)

                # Check if the image file exists
                if not os.path.isfile(full_path):
                    log_messages.append(f"Failed: Image file not found at {full_path} for product {product_id}")
                    error_count += 1
                    continue

                # Check if the file extension is allowed
                file_extension = os.path.splitext(full_path)[1].lower()
                if file_extension not in ALLOWED_IMAGE_EXTENSIONS:
                    log_messages.append(f"Failed: Invalid image file type '{file_extension}' for product {product_id}. Allowed types are {', '.join(ALLOWED_IMAGE_EXTENSIONS)}")
                    error_count += 1
                    continue

                try:
                    # Convert ID from export format to database ID
                    db_id = None
                    if product_id.startswith('__export__.product_template_'):
                        id_part = product_id.replace('__export__.product_template_', '').split('_')[0]
                        try:
                            db_id = int(id_part)
                        except ValueError:
                            log_messages.append(f"Failed: Invalid ID format {product_id}")
                            error_count += 1
                            continue
                    else:
                        try:
                            db_id = int(product_id)
                        except ValueError:
                            # Search using external ID
                            data = self.env['ir.model.data'].sudo().search([
                                ('model', '=', 'product.template'),
                                ('name', '=', product_id)
                            ], limit=1)
                            if data:
                                db_id = data.res_id
                            else:
                                log_messages.append(f"Failed: Could not convert ID {product_id} to database ID")
                                error_count += 1
                                continue

                    product = self.env['product.template'].browse(db_id)
                    if not product.exists():
                        log_messages.append(f"Failed: Product with ID {product_id} not found in the system")
                        error_count += 1
                        continue

                    # Read and encode the image to base64
                    with open(full_path, 'rb') as image_file:
                        image_data = base64.b64encode(image_file.read())

                    # Update the product
                    product.write({
                        self.image_field: image_data,
                    })
                    success_count += 1
                    log_messages.append(f"Success: Uploaded image for product {product.name} (ID: {product_id})")

                except Exception as e:
                    log_messages.append(f"Failed: Product {product_id} - {str(e)}")
                    _logger.error("Failed importing image for product %s: %s", product_id, str(e))
                    error_count += 1

        except Exception as e:
            log_messages.append(f"System Error: {str(e)}")
            _logger.error("System error during import: %s", str(e))
            error_count += 1

        # Summarize the results
        summary = f"Import Summary:\n- Successfully: {success_count}\n- Failed: {error_count}\n- Skipped: {skip_count}\n\n"
        self.import_log = summary + "\n".join(log_messages)
        self.state = 'result'

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    def action_reset(self):
        self.import_log = False
        self.state = 'choose'
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }