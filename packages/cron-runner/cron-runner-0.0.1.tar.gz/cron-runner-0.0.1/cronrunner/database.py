from peewee import *
import registry

database = MySQLDatabase(registry.config.get("db", section="database"),
                         user=registry.config.get("user", section="database"),
                         passwd=registry.config.get("passwd", section="database"),
                         host=registry.config.get("host", section="database"))


class BaseModel(Model):
    class Meta:
        database = database


class Job(BaseModel):
    command = CharField()
    locking = IntegerField()
    name = CharField(unique=True)
    notify = IntegerField()

    class Meta:
        db_table = 'job'


class Log(BaseModel):
    endtime = DateTimeField()
    error = TextField(null=True)
    job = IntegerField(db_column='job_id', index=True)
    output = TextField(null=True)
    returncode = IntegerField(null=True)
    starttime = DateTimeField()
    status = CharField()
    server = CharField()

    class Meta:
        db_table = 'log'
