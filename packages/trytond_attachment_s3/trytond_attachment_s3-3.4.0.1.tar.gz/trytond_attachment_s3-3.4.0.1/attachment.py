# -*- coding: utf-8 -*-
"""
    attachment

    Send attachments to S3

    :copyright: © 2012-2015 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""

try:
    import hashlib
except ImportError:
    hashlib = None
    import md5

from boto.s3.key import Key
from boto.s3.connection import S3Connection
from boto.exception import S3ResponseError

from trytond.config import config
from trytond.transaction import Transaction
from trytond.pool import PoolMeta

__all__ = ['Attachment']
__metaclass__ = PoolMeta


class Attachment:
    "Attachment"
    __name__ = 'ir.attachment'

    @classmethod
    def __setup__(cls):
        super(Attachment, cls).__setup__()

        cls._error_messages.update({
            "no_such_key": "File: %s with Key: %s doesn't exist in S3 bucket"
        })

    def get_data(self, name):
        """
        Get the data from S3 instead of filesystem.
        The filename is built as '<DBNAME>/<FILENAME>' in the given S3 bucket

        :param name: name of field name
        :return: Buffer of the file binary
        """
        s3_conn = S3Connection(
            config.get('attachment_s3', 'access_key'),
            config.get('attachment_s3', 'secret_key')
        )
        bucket = s3_conn.get_bucket(config.get('attachment_s3', 'bucket_name'))

        db_name = Transaction().cursor.dbname
        format_ = Transaction().context.pop(
            '%s.%s' % (self.__name__, name), ''
        )
        value = None
        if name == 'data_size' or format_ == 'size':
            value = 0
        if self.digest:
            filename = self.digest
            if self.collision:
                filename = filename + '-' + str(self.collision)
            filename = "/".join([db_name, filename])
            if name == 'data_size' or format_ == 'size':
                key = bucket.get_key(filename)
                if key is not None:
                    # Get the size only if bucket has key;
                    value = key.size
            else:
                k = Key(bucket)
                k.key = filename
                try:
                    value = buffer(k.get_contents_as_string())
                except S3ResponseError:
                    self.raise_user_error(
                        "no_such_key", error_args=(self.name, filename)
                    )
        return value

    @classmethod
    def set_data(cls, attachments, name, value):
        """
        Save the attachment to S3 instead of the filesystem

        :param attachments: List of ir.attachment instances
        :param name: name of the field
        :param value: binary data of the attachment (string)
        """
        s3_conn = S3Connection(
            config.get('attachment_s3', 'access_key'),
            config.get('attachment_s3', 'secret_key')
        )
        bucket = s3_conn.get_bucket(config.get('attachment_s3', 'bucket_name'))

        if value is None:
            return
        cursor = Transaction().cursor
        db_name = cursor.dbname

        if hashlib:
            digest = hashlib.md5(value).hexdigest()
        else:
            digest = md5.new(value).hexdigest()
        filename = "/".join([db_name, digest])
        collision = 0
        if bucket.get_key(filename):
            key2 = Key(bucket)
            key2.key = filename
            data2 = key2.get_contents_as_string()
            if value != data2:
                cursor.execute('SELECT DISTINCT(collision) '
                    'FROM ir_attachment '
                    'WHERE digest = %s '
                        'AND collision != 0 '
                    'ORDER BY collision', (digest,))
                collision2 = 0
                for row in cursor.fetchall():
                    collision2 = row[0]
                    filename = "/".join([
                        db_name, digest + '-' + str(collision2)
                    ])
                    if bucket.get_key(filename):
                        key2 = Key(bucket)
                        key2.key = filename
                        data2 = key2.get_contents_as_string()
                        if value == data2:
                            collision = collision2
                            break
                if collision == 0:
                    collision = collision2 + 1
                    filename = "/".join([
                        db_name, digest + '-' + str(collision)
                    ])
                    key = Key(bucket)
                    key.key = filename
                    key.set_contents_from_string(value[:])
        else:
            key = Key(bucket)
            key.key = filename
            key.set_contents_from_string(value[:])
        cls.write(attachments, {
            'digest': digest,
            'collision': collision,
        })
