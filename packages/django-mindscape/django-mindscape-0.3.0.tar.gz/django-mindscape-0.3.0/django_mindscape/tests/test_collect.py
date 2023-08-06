# -*- coding:utf-8 -*-
from evilunit import test_target
import unittest
from contextlib import contextmanager
from django_mindscape.tests.models import(X, Y, Group, Grade, Member)


@contextmanager
def with_rollback():
    from django.db import transaction
    with transaction.atomic():
        yield
        transaction.set_rollback(True)


@test_target("django_mindscape:Collector")
class Tests(unittest.TestCase):
    def _makeOne(self, models):
        from django_mindscape import ModelMapProvider, Walker
        mmprovider = ModelMapProvider(Walker(models))
        return self._getTarget()(mmprovider)

    def test_it_onetomany_sample(self):
        with with_rollback():
            g, h, r, s = Group.objects.bulk_create([
                Group(id=1, name="G"),
                Group(id=2, name="H"),
                Group(id=3, name="R"),
                Group(id=4, name="S"),
            ])
            g1, s1 = Grade.objects.bulk_create([
                Grade(id=1, name="1", group=g),
                Grade(id=2, name="1", group=s),
            ])
            hp, rw, dm = Member.objects.bulk_create([
                Member(id=1, name="HP", grade=g1),
                Member(id=2, name="RW", grade=g1),
                Member(id=3, name="DM", grade=s1)
            ])
            target = self._makeOne([Group, Member, Grade])
            result = target.collect(hp)

            self.assertIn(hp, result)
            self.assertIn(g1, result)
            self.assertIn(g, result)

    def test_it_with_missing_sample(self):
        with with_rollback():
            g1, = Grade.objects.bulk_create([
                Grade(id=1, name="1"),
            ])
            hp, rw = Member.objects.bulk_create([
                Member(id=1, name="HP", grade=g1),
                Member(id=2, name="RW", grade=g1),
            ])
            target = self._makeOne([Group, Member, Grade])
            result = target.collect(hp)

            self.assertIn(hp, result)
            self.assertIn(g1, result)

    def test_it_manytomany_sample(self):
        with with_rollback():
            """
            relation
            x0 - y0
            x0 - y1
            x1 - y1
            x2 - y2
            """
            with with_rollback():
                xs = X.objects.bulk_create([X(id=1), X(id=2), X(id=3)])
                ys = Y.objects.bulk_create([Y(id=1), Y(id=2), Y(id=3)])

                xs[0].ys.add(ys[0])
                xs[0].ys.add(ys[1])
                xs[1].ys.add(ys[1])
                xs[2].ys.add(ys[2])
                target = self._makeOne([X, Y])
                result = target.collect(ys[1])

                self.assertIn(xs[0], result)
                self.assertIn(xs[1], result)
                self.assertIn(ys[1], result)

    def test_it_manytomany_sample2(self):
        with with_rollback():
            """
            relation
            x0 - y0
            x0 - y1
            x1 - y1
            x2 - y2
            """
            with with_rollback():
                xs = X.objects.bulk_create([X(id=1), X(id=2), X(id=3)])
                ys = Y.objects.bulk_create([Y(id=1), Y(id=2), Y(id=3)])

                xs[0].ys.add(ys[0])
                xs[0].ys.add(ys[1])
                xs[1].ys.add(ys[1])
                xs[2].ys.add(ys[2])
                target = self._makeOne([X, Y])
                result = target.collect(xs[0])
                self.assertIn(xs[0], result)
                self.assertIn(ys[0], result)
                self.assertIn(ys[1], result)
