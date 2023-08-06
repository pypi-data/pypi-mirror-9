#!/usr/bin/env python
# coding=utf-8
from copy import deepcopy
from locale import setlocale, LC_ALL
from mongoengine.connection import connect
from mongoengine.document import EmbeddedDocument, Document
from mongoengine.fields import EmbeddedDocumentListField, StringField
from mls import mls
from uuid import uuid4
from weakref import proxy

__all__ = ["MultiLingualField"]


class MultiLingualEmbeddedDocument(EmbeddedDocument):
    language = StringField(required=True, min_length=2, max_length=3)
    value = StringField(required=True)


class MultiLingualField(EmbeddedDocumentListField):
    def __init__(self, **kwargs):
        super(MultiLingualField, self).__init__(
            MultiLingualEmbeddedDocument, **kwargs)

    def __set__(self, instance, value):
        if value is None:
            if self.null:
                value = None
            elif self.default is not None:
                value = self.default
                if callable(value):
                    value = value()

        if instance._initialised:
            try:
                if self.name not in instance._data \
                        or instance._data[self.name] != value \
                        or type(instance._data[self.name]) != type(value):
                    instance._mark_as_changed(self.name)
            except:
                instance._mark_as_changed(self.name)

        if isinstance(value, EmbeddedDocument):
            value._instance = proxy(instance)
        instance._data[self.name] = value

    def to_python(self, value):
        if isinstance(value, mls):
            return value

        value = super(MultiLingualField, self).to_python(value)

        return mls({
            item.language: item.value for item in value
        })

    def to_mongo(self, value):
        value = deepcopy(value)
        if isinstance(value, (dict, basestring)):
            value = mls(value)

        if isinstance(value, mls):
            return [
                {"language": key, "value": data}
                for key, data in value._mapping.items()
            ]

        return super(MultiLingualField, self).to_mongo(value)

    def validate(self, value):
        if isinstance(value, (list, tuple, set, frozenset)):
            for item in value:
                if not isinstance(item, dict) \
                        or "language" not in item \
                        or "value" not in item:
                    self.error("MultiLingualField accepts MultiLingualString, "
                               "list of dictionaries, dictionary or "
                               "string/unicode as it's value.")
        elif not isinstance(value, (mls, basestring, dict)):
            super(MultiLingualField, self).validate(value)


if __name__ == "__main__":
    class Country(Document):
        meta = {"collection": uuid4().hex}

        code = StringField(required=True, min_length=2, max_length=2)
        name = MultiLingualField(required=True)

    setlocale(LC_ALL, "en_US.UTF_8")
    connect("test")

    try:
        Country(
            code="ru", name=mls(ru=u"Россия", en="Russia", cs="Rusko")
        ).save()
        Country(
            code="cz", name=mls(ru=u"Чехия", en="Czech Republic", cs=u"Česko")
        ).save()

        ru = Country.objects.first()
        assert ru.code == "ru"
        assert str(ru.name) == "Russia"

        ru.name <<= "Russian Federation"
        ru.save()

        ru2 = Country.objects.first()
        assert repr(ru2.name) == "en'Russian Federation'"
        assert unicode(ru2.name >> "cs") == u"Rusko"

        cz = Country.objects[1]
        assert isinstance(cz.name, mls)

        cz.name = [
            {"language": "cs", "value": u"Česká republika"},
            {"language": "en", "value": "Czech Republic"},
            {"language": "ru", "value": u"Чешская Республика"},
        ]
        cz.save()

        cz2 = Country.objects[1]
        assert unicode(cz2.name >> "ru") == u"Чешская Республика"

        ru2.name = {
            "ru": u"Российская Федерация",
            "cs": u"Ruská federace",
            "en": "Russian Federation"
        }
        ru2.save()

        ru3 = Country.objects[0]
        assert unicode(ru3.name.translate_to("cs")) == u"Ruská federace"

        cz2.name = u"Czech Republic"  # Removing all mutations except en_US
        cz2.save()

        cz3 = Country.objects[1]
        assert str(cz3.name) == "Czech Republic"
        assert unicode(cz3.name >> "cs") == u"Czech Republic"

    finally:
        pass
        Country.drop_collection()
