# -*- coding:utf-8 -*-
import unittest


def normalize(target):
    if hasattr(target, "items"):
        return {k: normalize(v) for k, v in target.items()}
    else:
        return target


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from django_modelhint import testing
        from django_modelhint import MappingManager, setup
        d = cls.manager = MappingManager(reserved_words=[("label", "*default-label*")])
        setup(cls.manager)

        from django.db import models

        class Clan(models.Model):
            name = d.CharField(max_length=255, label="this-is-Clan-name")

            class Meta:
                app_label = __name__

        class Group(models.Model):
            name = d.CharField(max_length=255, label="this-is-Group-name")
            clan_set = d.ManyToManyField(Clan)

            class Meta:
                app_label = __name__

        class User(models.Model):
            group = d.ForeignKey(Group)
            name = d.CharField(max_length=255, label="this-is-User-name")
            age = d.IntegerField()

            class Meta:
                app_label = __name__

        cls.User = User
        cls.Group = Group
        cls.Clan = Clan
        testing.create_table(User)
        testing.create_table(Group)
        testing.create_table(Clan)

    def _getTarget(self):
        from django_modelhint import get_mapping
        return get_mapping

    def _callFUT(self, target):
        return self._getTarget()(target, mapping=self.manager)

    def test_it_model(self):
        user = self.User()
        result = self._callFUT(user)
        expected = {'name': {'label': 'this-is-User-name'},
                    'group': {'label': '*default-label*'},
                    'id': {'label': '*default-label*'},
                    'age': {'label': '*default-label*'}}
        self.assertEqual(normalize(result), expected)

    def test_it_relation(self):
        group = self.Group()
        result = self._callFUT(group.user_set)
        expected = {'name': {'label': 'this-is-User-name'},
                    'group': {'label': '*default-label*'},
                    'id': {'label': '*default-label*'},
                    'age': {'label': '*default-label*'}}
        self.assertEqual(normalize(result), expected)

    def test_it_relation2(self):
        clan = self.Clan()
        clan.save()
        group = self.Group()
        group.save()
        group.clan_set.add()
        result = self._callFUT(group.clan_set)
        expected = {'name': {'label': 'this-is-Clan-name'},
                    'id': {'label': '*default-label*'}}
        self.assertEqual(normalize(result), expected)

    def test_it_field(self):
        user = self.User()
        result = self._callFUT(user._meta.get_field("name"))
        expected = {'label': 'this-is-User-name'}
        self.assertEqual(normalize(result), expected)

    def test_it_modify_free(self):
        user = self.User()
        result = self._callFUT(user._meta.get_field("name"))
        result.pop("label", None)
        result = self._callFUT(user._meta.get_field("name"))
        expected = {'label': 'this-is-User-name'}
        self.assertEqual(normalize(result), expected)
