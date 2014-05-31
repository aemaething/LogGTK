from Models import LogEntry
from peewee_fake_fixtures import *
from faker import Factory
import datetime


def add_fake_content():
    fake = Factory.create()
    for i in range(1, 50):
        fake_fixture({
            LogEntry: {
                'title': fake.sentence(),
                'content': "\n".join(fake.paragraphs(3)),
                'created_at': datetime.datetime.now()
                              - datetime.timedelta(
                                    days=random.randint(1, 365),
                                    hours=random.randint(1,24),
                                    minutes=random.randint(1, 59)),
                'updated_at': datetime.datetime.now()
                              - datetime.timedelta(
                                    days=random.randint(1, 365),
                                    hours=random.randint(1,24),
                                    minutes=random.randint(1, 59))
            }},
            on_failure=lambda x, y, z: fake_fixture_drop(z)
        )
