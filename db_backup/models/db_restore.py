import os
import zipfile
import json
import logging
import tempfile
import shutil
from odoo import models, fields, api, _, tools
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class DatabaseRestore(models.Model):
    _name = 'db.restore'
    _description = 'Database Restore'

    name = fields.Char('Description', required=True)
    master_password = fields.Char('Master Password', required=True)
    new_db_name = fields.Char('New Database Name', required=True)
    server_file_path = fields.Selection(
        selection='_get_available_backups',
        string='Server Backup File',
        required=True
    )

    @api.model
    def _get_available_backups(self):
        backup_dir = self.env['db.backup'].search([], limit=1).backup_dir
        if not backup_dir or not os.path.exists(backup_dir):
            return []
        
        files = []
        for file in os.listdir(backup_dir):
            if file.endswith('.zip'):
                files.append((os.path.join(backup_dir, file), file))
        return files

    def _validate_backup_file(self, file_path):
        try:
            with zipfile.ZipFile(file_path) as z:
                required_files = ['dump.sql', 'manifest.json', 'filestore']
                zip_files = z.namelist()
                
                for req_file in required_files:
                    if not any(f.startswith(req_file) for f in zip_files):
                        raise UserError(_(f"Missing required file: {req_file}"))
                
                with z.open('manifest.json') as f:
                    manifest = json.load(f)
                    if 'version' not in manifest or 'modules' not in manifest:
                        raise UserError(_("Invalid manifest.json format"))
                
                return True
        except zipfile.BadZipFile:
            raise UserError(_("Invalid backup file format"))
        except Exception as e:
            raise UserError(_("Error validating backup file: %s") % str(e))

    def action_restore_database(self):
        self.ensure_one()
        _logger.error("=== Starting restore process ===")
        
        try:
            from odoo.service import db
            from odoo.tools.misc import str2bool

            # 1. ตรวจสอบพารามิเตอร์
            if not self.server_file_path:
                raise UserError("No backup file selected")
            if not self.new_db_name:
                raise UserError("No new database name specified")
            if not self.master_password:
                raise UserError("Master password is required")

            # 2. ตรวจสอบฐานข้อมูล
            if self.new_db_name in db.list_dbs():
                raise UserError(f"Database {self.new_db_name} already exists!")

            _logger.error(f"Selected backup file: {self.server_file_path}")
            _logger.error(f"New database name: {self.new_db_name}")

            # 3. ทำการ restore
            try:
                with open(self.server_file_path, 'rb') as f:
                    _logger.error("Starting database restore")
                    db.restore_db(self.new_db_name, f, self.master_password)
                    _logger.error("Database restore completed")
            except Exception as e:
                _logger.error(f"Restore error: {str(e)}")
                raise UserError(f"Error during restore: {str(e)}")

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Database restored successfully! Please restart Odoo server.'),
                    'type': 'success',
                    'sticky': True,
                }
            }

        except Exception as e:
            _logger.error(f"Restore failed with error: {str(e)}", exc_info=True)
            raise UserError(f"Restore failed: {str(e)}")