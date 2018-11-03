from CTFd.utils import get_app_config, get_config, set_config
from CTFd.utils.migrations import get_current_revision
from CTFd.models import db, get_class_by_tablename
from datafreeze.format import SERIALIZERS
from flask import current_app as app
from datafreeze.format.fjson import JSONSerializer, JSONEncoder
import dataset
import datafreeze
import datetime
import json
import os
import re
import six
import shutil
import zipfile


class CTFdSerializer(JSONSerializer):
    """
    Slightly modified datafreeze serializer so that we can properly
    export the CTFd database into a zip file.
    """

    def close(self):
        for path, result in self.buckets.items():
            result = self.wrap(result)

            if self.fileobj is None:
                fh = open(path, 'wb')
            else:
                fh = self.fileobj

            data = json.dumps(result,
                              cls=JSONEncoder,
                              indent=self.export.get_int('indent'))

            callback = self.export.get('callback')
            if callback:
                data = "%s && %s(%s);" % (callback, callback, data)

            if six.PY3:
                fh.write(bytes(data, encoding='utf-8'))
            else:
                fh.write(data)
            if self.fileobj is None:
                fh.close()


SERIALIZERS['ctfd'] = CTFdSerializer  # Load the custom serializer


def export_ctf():
    db = dataset.connect(get_app_config('SQLALCHEMY_DATABASE_URI'))

    # Backup database
    backup = six.BytesIO()

    backup_zip = zipfile.ZipFile(backup, 'w')

    tables = db.tables
    for table in tables:
        result = db[table].all()
        result_file = six.BytesIO()
        datafreeze.freeze(result, format='ctfd', fileobj=result_file)
        result_file.seek(0)
        backup_zip.writestr('db/{}.json'.format(table), result_file.read())

    # # Guarantee that alembic_version is saved into the export
    if 'alembic_version' not in tables:
        result = {
            "count": 1,
            "results": [
                {
                    "version_num": get_current_revision()
                }
            ],
            "meta": {}
        }
        result_file = six.BytesIO()
        json.dump(result, result_file)
        result_file.seek(0)
        backup_zip.writestr('db/alembic_version.json', result_file.read())

    # Backup uploads
    upload_folder = os.path.join(os.path.normpath(app.root_path), app.config.get('UPLOAD_FOLDER'))
    for root, dirs, files in os.walk(upload_folder):
        for file in files:
            parent_dir = os.path.basename(root)
            backup_zip.write(os.path.join(root, file), arcname=os.path.join('uploads', parent_dir, file))

    backup_zip.close()
    backup.seek(0)
    return backup


def import_ctf(backup):
    if not zipfile.is_zipfile(backup):
        raise zipfile.BadZipfile

    side_db = dataset.connect(get_app_config('SQLALCHEMY_DATABASE_URI'))
    sqlite = get_app_config('SQLALCHEMY_DATABASE_URI').startswith('sqlite')

    backup = zipfile.ZipFile(backup)

    members = backup.namelist()
    max_content_length = get_app_config('MAX_CONTENT_LENGTH')
    for f in members:
        if f.startswith('/') or '..' in f:
            # Abort on malicious zip files
            raise zipfile.BadZipfile
        info = backup.getinfo(f)
        if max_content_length:
            if info.file_size > max_content_length:
                raise zipfile.LargeZipFile

    for member in members:
        if member.startswith('db/'):
            table_name = member[3:-5]
            data = backup.open(member).read()
            if data:
                table = side_db[table_name]

                if sqlite:
                    db.session.execute('DELETE FROM ' + table_name)
                else:
                    db.session.execute('TRUNCATE TABLE '+table_name)
                db.session.commit()
                saved = json.loads(data)
                for entry in saved['results']:
                    # This is a hack to get SQLite to properly accept datetime values from dataset
                    # See Issue #246
                    if sqlite:
                        for k, v in entry.items():
                            if isinstance(v, six.string_types):
                                match = re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d", v)
                                if match:
                                    entry[k] = datetime.datetime.strptime(v, '%Y-%m-%dT%H:%M:%S.%f')
                                    continue
                                match = re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", v)
                                if match:
                                    entry[k] = datetime.datetime.strptime(v, '%Y-%m-%dT%H:%M:%S')
                                    continue
                    table.insert(entry)

    # Extracting files
    files = [f for f in backup.namelist() if f.startswith('uploads/')]
    upload_folder = app.config.get('UPLOAD_FOLDER')
    for f in files:
        filename = f.split(os.sep, 1)

        if len(filename) < 2:  # just an empty uploads directory (e.g. uploads/)
            continue

        filename = filename[1]  # Get the second entry in the list (the actual filename)
        full_path = os.path.join(upload_folder, filename)
        dirname = os.path.dirname(full_path)

        # Create any parent directories for the file
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        source = backup.open(f)
        target = open(full_path, "wb")
        with source, target:
            shutil.copyfileobj(source, target)
