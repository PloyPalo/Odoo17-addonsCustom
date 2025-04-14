import os
import datetime
import pytz
import json
import logging
import psycopg2
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import subprocess
import shutil

_logger = logging.getLogger(__name__)

class DatabaseBackup(models.Model):
  _name = 'db.backup'
  _description = 'Database Backup'

  filestore_path = fields.Char(
      'Filestore Path',
      required=True,
      default='C:\\Program Files\\Odoo17\\sessions\\filestore'
  )
  pg_dump_path = fields.Char(
      'Path to pg_dump.exe',
      required=True,
      default='C:\\Program Files\\Odoo17\\PostgreSQL\\bin\\pg_dump.exe'
  )

  name = fields.Char('Name', required=True)
  db_name = fields.Selection(selection='_get_db_list', string='Database Name', required=True)
  backup_dir = fields.Char('Backup Directory', required=True, default='D:\\DB_Backup')
  backup_type = fields.Selection([
      ('manual', 'Manual'),
      ('scheduled', 'Scheduled')
  ], string='Backup Type', default='manual', required=True)
  active = fields.Boolean(default=True)
  
  # PostgreSQL Credentials
  pg_host = fields.Char('PostgreSQL Host', default='localhost')
  pg_port = fields.Char('PostgreSQL Port', default='5432')
  pg_user = fields.Char('PostgreSQL User', required=True)
  pg_password = fields.Char('PostgreSQL Password', required=True)
  
  # Schedule fields
  schedule_interval = fields.Selection([
      ('daily', 'Daily'),
      ('weekly', 'Weekly'),
      ('monthly', 'Monthly')
  ], string='Backup Frequency')
  
  backup_time = fields.Selection([
      ('00:00', '00:00'), ('01:00', '01:00'), ('02:00', '02:00'),
      ('03:00', '03:00'), ('04:00', '04:00'), ('05:00', '05:00'),
      ('06:00', '06:00'), ('07:00', '07:00'), ('08:00', '08:00'),
      ('09:00', '09:00'), ('10:00', '10:00'), ('11:00', '11:00'),
      ('12:00', '12:00'), ('13:00', '13:00'), ('14:00', '14:00'),
      ('15:00', '15:00'), ('16:00', '16:00'), ('17:00', '17:00'),
      ('18:00', '18:00'), ('19:00', '19:00'), ('20:00', '20:00'),
      ('21:00', '21:00'), ('22:00', '22:00'), ('23:00', '23:00')
  ], string='Backup Time')
  
  week_day = fields.Selection([
      ('0', 'Monday'),
      ('1', 'Tuesday'),
      ('2', 'Wednesday'),
      ('3', 'Thursday'),
      ('4', 'Friday'),
      ('5', 'Saturday'),
      ('6', 'Sunday')
  ], string='Day of Week')
  
  month_day = fields.Selection([
      (str(x), str(x)) for x in range(1, 32)
  ], string='Day of Month')
  
  next_backup = fields.Datetime('Next Backup', compute='_compute_next_backup', store=True)

  def _validate_paths(self):
      if not self.pg_dump_path or not os.path.exists(self.pg_dump_path):
          raise UserError(_("pg_dump path not found: %s") % self.pg_dump_path)
   
      if not self.filestore_path or not os.path.exists(self.filestore_path):
          raise UserError(_("Filestore path not found: %s") % self.filestore_path)

  @api.onchange('backup_type')
  def _onchange_backup_type(self):
      if self.backup_type == 'manual':
          self.schedule_interval = False
          self.backup_time = False
          self.week_day = False
          self.month_day = False

  @api.model
  def _get_db_list(self):
      try:
          conn = psycopg2.connect(
              dbname='postgres',
              user=self.env['ir.config_parameter'].sudo().get_param('db_backup.pg_user', 'odoo'),
              password=self.env['ir.config_parameter'].sudo().get_param('db_backup.pg_password', 'odoo'),
              host=self.env['ir.config_parameter'].sudo().get_param('db_backup.pg_host', 'localhost'),
              port=self.env['ir.config_parameter'].sudo().get_param('db_backup.pg_port', '5432')
          )
          conn.autocommit = True
          cur = conn.cursor()
          cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
          db_list = cur.fetchall()
          cur.close()
          conn.close()
          return [(db[0], db[0]) for db in db_list]
      except Exception as e:
          _logger.error("Error getting database list: %s", str(e))
          return [(self.env.cr.dbname, self.env.cr.dbname)]

  @api.model
  def create(self, vals):
      if vals.get('pg_user'):
          self.env['ir.config_parameter'].sudo().set_param('db_backup.pg_user', vals['pg_user'])
      if vals.get('pg_password'):
          self.env['ir.config_parameter'].sudo().set_param('db_backup.pg_password', vals['pg_password'])
      if vals.get('pg_host'):
          self.env['ir.config_parameter'].sudo().set_param('db_backup.pg_host', vals['pg_host'])
      if vals.get('pg_port'):
          self.env['ir.config_parameter'].sudo().set_param('db_backup.pg_port', vals['pg_port'])
      return super(DatabaseBackup, self).create(vals)

  def write(self, vals):
      if vals.get('pg_user'):
          self.env['ir.config_parameter'].sudo().set_param('db_backup.pg_user', vals['pg_user'])
      if vals.get('pg_password'):
          self.env['ir.config_parameter'].sudo().set_param('db_backup.pg_password', vals['pg_password'])
      if vals.get('pg_host'):
          self.env['ir.config_parameter'].sudo().set_param('db_backup.pg_host', vals['pg_host'])
      if vals.get('pg_port'):
          self.env['ir.config_parameter'].sudo().set_param('db_backup.pg_port', vals['pg_port'])
      return super(DatabaseBackup, self).write(vals)
    
  def copy(self, default=None):
      default = dict(default or {})
    
      # ตรวจสอบว่าฐานข้อมูลที่จะ copy ยังมีอยู่ในระบบหรือไม่
      db_list = dict(self._get_db_list())
      if self.db_name not in db_list:
        # ถ้าไม่มี ให้ใช้ฐานข้อมูลปัจจุบันหรือฐานข้อมูลแรกในรายการ
        default['db_name'] = self.env.cr.dbname if self.env.cr.dbname in db_list else list(db_list.keys())[0] if db_list else False
    
      # ตั้งชื่อใหม่เพื่อไม่ให้ซ้ำ
      default['name'] = _("%s (copy)") % self.name
    
      return super(DatabaseBackup, self).copy(default)


  def _get_local_time(self):
      """Get current time in user's timezone"""
      user_tz = pytz.timezone(self.env.user.tz or 'UTC')
      return datetime.datetime.now(user_tz)

  def _convert_to_local_time(self, utc_dt):
      """Convert UTC datetime to local timezone"""
      user_tz = pytz.timezone(self.env.user.tz or 'UTC')
      return pytz.utc.localize(utc_dt).astimezone(user_tz)

  @api.depends('schedule_interval', 'backup_time', 'week_day', 'month_day')
  def _compute_next_backup(self):
      for record in self:
          if record.backup_type != 'scheduled' or not record.backup_time:
              record.next_backup = False
              continue

          local_now = self._get_local_time()
          backup_hour = int(record.backup_time.split(':')[0])
          
          # แก้ไขส่วนนี้ - ใช้ backup_hour ในการคำนวณวันถัดไป
          next_backup = local_now.replace(
              hour=backup_hour,
              minute=0,
              second=0,
              microsecond=0
          )

          if next_backup.time() <= local_now.time():
              next_backup += datetime.timedelta(days=1)

          if record.schedule_interval == 'daily':
              pass
          
          elif record.schedule_interval == 'weekly' and record.week_day:
              target_weekday = int(record.week_day)
              current_weekday = next_backup.weekday()
              days_ahead = target_weekday - current_weekday
              
              if days_ahead < 0:
                  days_ahead += 7
              elif days_ahead == 0 and next_backup.time() <= local_now.time():
                  days_ahead = 7
              
              next_backup += datetime.timedelta(days=days_ahead)
          
          elif record.schedule_interval == 'monthly' and record.month_day:
              target_day = int(record.month_day)
              
              try:
                  next_backup = next_backup.replace(day=target_day)
                  if next_backup < local_now:
                      if next_backup.month == 12:
                          # แก้ไขส่วนนี้ - รักษาค่า hour ไว้
                          next_backup = next_backup.replace(year=next_backup.year + 1, month=1, hour=backup_hour)
                      else:
                          # แก้ไขส่วนนี้ - รักษาค่า hour ไว้
                          next_backup = next_backup.replace(month=next_backup.month + 1, hour=backup_hour)
              except ValueError:
                  if next_backup.month == 12:
                      # แก้ไขส่วนนี้ - รักษาค่า hour ไว้
                      next_backup = next_backup.replace(year=next_backup.year + 1, month=1, day=target_day, hour=backup_hour)
                  else:
                      # แก้ไขส่วนนี้ - รักษาค่า hour ไว้
                      next_backup = next_backup.replace(month=next_backup.month + 1, day=target_day, hour=backup_hour)

          record.next_backup = next_backup.astimezone(pytz.UTC).replace(tzinfo=None)

  def action_backup_database(self):
      self.ensure_one()
      self._validate_paths()  # ตรวจสอบ paths ก่อน
      
      if not os.path.exists(self.backup_dir):
          os.makedirs(self.backup_dir)

      local_time = self._get_local_time()  # ใช้เวลาท้องถิ่น
    
      # ใช้เวลาปัจจุบันเสมอสำหรับการตั้งชื่อไฟล์
      timestamp = local_time.strftime('%Y-%m-%d-%H%M%S')
    
      backup_name = f"{self.db_name}-{timestamp}"       
      backup_path = os.path.join(self.backup_dir, backup_name)
    
      temp_dir = os.path.join(self.backup_dir, 'temp_' + backup_name)
      os.makedirs(temp_dir)
        
      try:
          # 1. Dump database to SQL file
          sql_file = os.path.join(temp_dir, 'dump.sql')
          _logger.info("Creating dump file at: %s", sql_file)

          # การสร้างคำสั่ง pg_dump
          env = os.environ.copy()
          env['PGPASSWORD'] = self.pg_password
          
          cmd_dump = [
              self.pg_dump_path,
              '-h', self.pg_host,
              '-p', self.pg_port,
              '-U', self.pg_user,
              '-d', self.db_name,
              '-f', sql_file,
              '-F', 'p'
          ]
          
          _logger.info("Running pg_dump command: %s", ' '.join(cmd_dump))
          
          process = subprocess.Popen(
              cmd_dump,
              stdout=subprocess.PIPE,
              stderr=subprocess.PIPE,
              env=env,  # ใช้ env ที่มีการกำหนด PGPASSWORD
              shell=True  # เพิ่ม shell=True สำหรับ Windows
          )
          output, error = process.communicate()
          
          if process.returncode != 0:
              _logger.error("pg_dump error output: %s", error.decode())
              raise UserError(_("Database dump failed! Error: %s") % error.decode())
          
          if not os.path.exists(sql_file):
              raise UserError(_("Dump file was not created at: %s") % sql_file)

          # 2. Copy filestore
          filestore_source = os.path.join(self.filestore_path, self.db_name)
        
          _logger.info("Full filestore path: %s", os.path.abspath(filestore_source))
          if not os.path.exists(filestore_source):
              raise UserError(_("Could not find filestore directory at: %s") % filestore_source)

          filestore_backup = os.path.join(temp_dir, 'filestore')

          try:
              _logger.info("Copying filestore to: %s", filestore_backup)
              shutil.copytree(filestore_source, filestore_backup, dirs_exist_ok=True)
              
              # ตรวจสอบว่า copy สำเร็จ
              if not os.path.exists(filestore_backup) or not os.listdir(filestore_backup):
                  raise UserError(_("Failed to copy filestore or filestore is empty"))
              
              _logger.info("Filestore copied successfully")
          except Exception as e:
              _logger.error("Error copying filestore: %s", str(e))
              raise UserError(_("Failed to copy filestore: %s") % str(e)) 

          # 3. Create manifest.json
          manifest = {
              'odoo_dump': "1",
              'db_name': self.db_name,
              'version': f"17.0-{datetime.datetime.now().strftime('%Y%m%d')}",
              'version_info': [17, 0, 0, "final", 0, ""],
              'major_version': "17.0",
              'pg_version': "12.0",
              'modules': {}
          }

          modules = self.env['ir.module.module'].sudo().search([
              ('state', '=', 'installed')
          ])
          for module in modules:
              manifest['modules'][module.name] = module.installed_version or '0.0'

          manifest_file = os.path.join(temp_dir, 'manifest.json')
          with open(manifest_file, 'w') as f:
              json.dump(manifest, f, indent=4)

          # 4. Create ZIP file
          zip_file = backup_path + '.zip'
          if os.path.exists(zip_file):
              os.remove(zip_file)

          def zipdir(path, ziph):
              for root, dirs, files in os.walk(path):
                  for file in files:
                      file_path = os.path.join(root, file)
                      arcname = os.path.relpath(file_path, path)
                      _logger.info("Adding to zip: %s as %s", file_path, arcname)
                      ziph.write(file_path, arcname)

          import zipfile
          with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
              zipdir(temp_dir, zipf)

          _logger.info("ZIP file created at: %s", zip_file)

          return {
              'type': 'ir.actions.client',
              'tag': 'display_notification',
              'params': {
                  'title': _('Success'),
                  'message': _('Database backup completed successfully!'),
                  'type': 'success',
              }
          }

      except Exception as e:
          _logger.error("Backup failed with error: %s", str(e))
          raise UserError(_("Backup failed! Error: %s") % str(e))
      
      finally:
          if os.path.exists(temp_dir):
              shutil.rmtree(temp_dir)

  @api.model
  def _run_scheduled_backup(self):
      _logger.info("====== STARTING SCHEDULED BACKUP CHECK ======")
      backups = self.search([
          ('backup_type', '=', 'scheduled'),
          ('active', '=', True)
      ])

      _logger.info("Found %s scheduled backups active in system", len(backups))

      now = fields.Datetime.now()
      _logger.info("Current time (UTC): %s", now)
      
      for backup in backups:
          _logger.info("Checking backup '%s' (id: %s)", backup.name, backup.id)
          _logger.info("Next backup time: %s", backup.next_backup)
          _logger.info("Backup settings: type=%s, frequency=%s, time=%s", 
                       backup.backup_type, backup.schedule_interval, backup.backup_time)
          if backup.next_backup and backup.next_backup <= now:
            _logger.info("Time to backup! Executing backup for '%s'", backup.name)
            try:
                backup.action_backup_database()
                _logger.info("Backup completed successfully")
                backup._compute_next_backup()
                _logger.info("Next backup scheduled for: %s", backup.next_backup)
            except Exception as e:
                _logger.error("Backup failed with error: %s", str(e), exc_info=True)
          else:
              _logger.info("Not yet time for backup '%s'", backup.name)
    
      _logger.info("====== COMPLETED SCHEDULED BACKUP CHECK ======")

  @api.model
  def run_all_scheduled_backups(self):
      """Run all scheduled backups immediately, regardless of their scheduled time"""
      _logger.info("Manually running all scheduled backups...")
      backups = self.search([
          ('backup_type', '=', 'scheduled'),
          ('active', '=', True)
      ])
      
      count = 0
      for backup in backups:
          _logger.info("Running backup for %s", backup.name)
          try:
              backup.action_backup_database()
              _logger.info("Backup completed successfully")
              backup._compute_next_backup()
              count += 1
          except Exception as e:
              _logger.error("Backup failed: %s", str(e), exc_info=True)
      
      return {
          'type': 'ir.actions.client',
          'tag': 'display_notification',
          'params': {
              'title': _('Backup Process'),
              'message': _('%s scheduled backups processed') % count,
              'type': 'success',
          }
      }