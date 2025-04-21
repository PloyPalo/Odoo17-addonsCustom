import os
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import logging

_logger = logging.getLogger(__name__)

class DatabaseDownload(models.TransientModel):
    _name = 'db.download'
    _description = 'Download Database Backup'

    backup_files = fields.Selection('_get_backup_files', string='Backup Files', required=True)
    backup_file_content = fields.Binary('Backup File', attachment=False)
    backup_file_name = fields.Char('File Name')

    @api.model
    def _get_backup_files(self):
        # แก้ไขการค้นหาไดเร็กทอรีสำรองข้อมูล
        backup_configs = self.env['db.backup'].search([], limit=1)
        if not backup_configs:
            _logger.error("No backup configuration found")
            return []
            
        backup_dir = backup_configs.backup_dir
        _logger.info("Looking for backups in: %s", backup_dir)
        
        if not backup_dir or not os.path.exists(backup_dir):
            _logger.error("Backup directory does not exist: %s", backup_dir)
            return []
            
        try:
            files = []
            for file in os.listdir(backup_dir):
                if file.endswith('.zip'):
                    _logger.info("Found backup file: %s", file)
                    files.append((file, file))
            
            if not files:
                _logger.warning("No backup files found in %s", backup_dir)
                
            return files
        except Exception as e:
            _logger.error("Error reading backup files: %s", str(e))
            return []

    @api.model
    def default_get(self, fields):
        # เพิ่มฟังก์ชันเพื่อให้ค่าเริ่มต้นถูกโหลดเมื่อเปิดวิซาร์ด
        res = super(DatabaseDownload, self).default_get(fields)
        backup_files = dict(self._get_backup_files())
        if backup_files:
            res['backup_files'] = list(backup_files.keys())[0]
        return res

    def refresh_backup_list(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'db.download',
            'view_mode': 'tree',
            'target': 'current',
            'views': [(False, 'tree')],
        }   

    def download_backup(self):
        self.ensure_one()
        if not self.backup_files:
            raise UserError(_("Please select a backup file to download"))
        
        backup_configs = self.env['db.backup'].search([], limit=1)
        if not backup_configs:
            raise UserError(_("No backup configuration found"))
            
        backup_dir = backup_configs.backup_dir
        file_path = os.path.join(backup_dir, self.backup_files)
        
        if not os.path.exists(file_path):
            raise UserError(_("Backup file not found: %s") % file_path)
            
        try:
            with open(file_path, 'rb') as f:
                self.backup_file_content = base64.b64encode(f.read())
            self.backup_file_name = self.backup_files
            
            return {
                'type': 'ir.actions.act_url',
                'url': '/web/content/?model=db.download&id=%s&filename=%s&field=backup_file_content&download=true' % (self.id, self.backup_file_name),
                'target': 'self',
            }
            self.unlink()  # ลบ record หลังจากดาวน์โหลด
            return action
        except Exception as e:
            raise UserError(_("Error downloading backup: %s") % str(e))
