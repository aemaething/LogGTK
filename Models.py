from peewee import *
import datetime

database = SqliteDatabase('database-file.db')


class BaseModel(Model):
    """ base model of all app models """
    class Meta:
        """ base models meta data """
        database = database


class LogEntry(BaseModel):
    """ model of log entry """
    title = CharField()
    content = CharField()
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=None, null=True)

    def __repr__(self):
        return '%s: %s' % (self.created_at.strftime("%Y-%m-%d %H:%M:%S"), self.title)

    class Meta:
        """ models metadata """
        order_by = ('-created_at',)
        db_table = 'log_entries'
