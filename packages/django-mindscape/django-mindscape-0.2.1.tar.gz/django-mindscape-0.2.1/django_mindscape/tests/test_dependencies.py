# -*- coding:utf-8 -*-
import unittest
from evilunit import test_target


@test_target("django_mindscape:Walker")
class ForeignKeyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from django.db import models

        class Group(models.Model):
            name = models.CharField(max_length=255, null=False, default="")

            class Meta:
                app_label = "myapp"

        class Member(models.Model):
            group = models.ForeignKey(Group)
            name = models.CharField(max_length=255, null=False, default="")

            class Meta:
                app_label = "myapp"

        cls.Group = Group
        cls.Member = Member

    def _get_models(self):
        return [self.Group, self.Member]

    def test_dependecies__member(self):
        walker = self._makeOne(self._get_models())
        walker.walkall()

        member_dependencies = [node.to.model for node in walker[self.Member].dependencies]
        self.assertEqual(member_dependencies, [self.Group])

    def test_dependecies__group(self):
        walker = self._makeOne(self._get_models())
        walker.walkall()

        self.assertEqual(walker[self.Group].dependencies, [])

    def test_relation_type(self):
        walker = self._makeOne(self._get_models())
        walker.walkall()

        reltype = walker[self.Member].dependencies[0].type
        self.assertEqual(reltype, "M1")

    def test_relation_name(self):
        walker = self._makeOne(self._get_models())
        walker.walkall()

        name = walker[self.Member].dependencies[0].name
        self.assertEqual(name, "group")

    def test_relation_backref(self):
        walker = self._makeOne(self._get_models())
        walker.walkall()

        backref = walker[self.Member].dependencies[0].backref
        self.assertEqual(backref, "member_set")


@test_target("django_mindscape:Walker")
class RelatedNameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from django.db import models

        class Group(models.Model):
            name = models.CharField(max_length=255, null=False, default="")

            class Meta:
                app_label = "myappp"

        class Member(models.Model):
            group = models.ForeignKey(Group, related_name="+")
            name = models.CharField(max_length=255, null=False, default="")

            class Meta:
                app_label = "myappp"

        cls.Group = Group
        cls.Member = Member

    def _get_models(self):
        return [self.Group, self.Member]

    def test_relation_name(self):
        walker = self._makeOne(self._get_models())
        walker.walkall()

        name = walker[self.Member].dependencies[0].name
        self.assertEqual(name, "group")

    def test_relation_backref(self):
        walker = self._makeOne(self._get_models())
        walker.walkall()

        backref = walker[self.Member].dependencies[0].backref
        self.assertEqual(backref, None)


@test_target("django_mindscape:Walker")
class ManyToManyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from django.db import models

        class Group(models.Model):
            name = models.CharField(max_length=255, null=False, default="")

            class Meta:
                app_label = "myapp2"

        class Member(models.Model):
            group_set = models.ManyToManyField(Group, through="GroupToMember")
            name = models.CharField(max_length=255, null=False, default="")

            class Meta:
                app_label = "myapp2"

        class GroupToMember(models.Model):
            member = models.ForeignKey(Member)
            group = models.ForeignKey(Group)

            class Meta:
                app_label = "myapp2"

        cls.Group = Group
        cls.Member = Member
        cls.GroupToMember = GroupToMember

    def _get_models(self):
        return [self.Group, self.Member]

    def test_relation_type(self):
        walker = self._makeOne(self._get_models())
        walker.walkall()
        reltype = walker[self.Member].dependencies[0].type
        self.assertEqual(reltype, "MM")

    def test_relation_name(self):
        walker = self._makeOne(self._get_models())
        walker.walkall()

        name = walker[self.Member].dependencies[0].name
        self.assertEqual(name, "group_set")

    def test_relation_backref(self):
        walker = self._makeOne(self._get_models())
        walker.walkall()

        backref = walker[self.Member].dependencies[0].backref
        self.assertEqual(backref, "member_set")

    def test_relation_through(self):
        walker = self._makeOne(self._get_models())
        walker.walkall()

        through = walker[self.Member].dependencies[0].through
        self.assertEqual(through.model, self.GroupToMember)


@test_target("django_mindscape:Walker")
class OneToOneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from django.db import models

        class Group(models.Model):
            name = models.CharField(max_length=255, null=False, default="")

            class Meta:
                app_label = "myapp3"

        class Member(models.Model):
            group = models.OneToOneField(Group)
            name = models.CharField(max_length=255, null=False, default="")

            class Meta:
                app_label = "myapp3"

        cls.Group = Group
        cls.Member = Member

    def _get_models(self):
        return [self.Group, self.Member]

    def test_relation_type(self):
        walker = self._makeOne(self._get_models())
        walker.walkall()
        reltype = walker[self.Member].dependencies[0].type
        self.assertEqual(reltype, "11")

    def test_relation_name(self):
        walker = self._makeOne(self._get_models())
        walker.walkall()

        name = walker[self.Member].dependencies[0].name
        self.assertEqual(name, "group")

    def test_relation_backref(self):
        walker = self._makeOne(self._get_models())
        walker.walkall()

        backref = walker[self.Member].dependencies[0].backref
        self.assertEqual(backref, "member")
