# -*- coding:utf-8 -*-
import unittest
from evilunit import test_target


@test_target("django_mindscape:ModelMapProvider")
class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from django.db import models

        class Group(models.Model):
            name = models.CharField(max_length=255, null=False, default="")

            class Meta:
                app_label = __name__

        class Member(models.Model):
            group = models.ForeignKey(Group)
            name = models.CharField(max_length=255, null=False, default="")

            class Meta:
                app_label = __name__

        class Shop(models.Model):
            name = models.CharField(max_length=255, null=False, default="")

            class Meta:
                app_label = __name__

        cls.Group = Group
        cls.Member = Member
        cls.Shop = Shop

    def _makeOne(self, models):
        from django_mindscape import Walker, Brain
        walker = Walker(models, brain=Brain(), bidirection=False)
        return self._getTarget()(walker)

    def test_it_dependencies(self):
        target = self._makeOne([self.Group, self.Member, self.Shop])

        ds = target.dependencies
        self.assertEqual(ds[self.Group].dependencies, [])
        self.assertEqual(ds[self.Shop].dependencies, [])
        self.assertEqual([r.from_.model for r in ds[self.Member].dependencies], [self.Member])
        self.assertEqual([r.to.model for r in ds[self.Member].dependencies], [self.Group])

    def test_it_reverse_dependencies(self):
        target = self._makeOne([self.Group, self.Member, self.Shop])

        rds = target.reverse_dependencies
        self.assertEqual([rn.node.model for rn in rds[self.Group].children], [self.Member])
        self.assertEqual(rds[self.Shop].children, [])
        self.assertEqual(rds[self.Member].children, [])

    def test_it_ordered_models(self):
        target = self._makeOne([self.Group, self.Member, self.Shop])

        models = target.ordered_models
        self.assertEqual(models, [self.Group, self.Member, self.Shop])

    def test_it_cluster_models(self):
        target = self._makeOne([self.Group, self.Member, self.Shop])

        models = target.cluster_models
        self.assertEqual(models, [[self.Group, self.Member], [self.Shop]])
