import unittest
from evilunit import test_target


@test_target("django_mindscape:BidirectionalWalker")
class Bidirectional_ForeignKeyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from django.db import models

        class Group_(models.Model):
            name = models.CharField(max_length=255, null=False, default="")

            class Meta:
                app_label = __name__

        class Member_(models.Model):
            group = models.ForeignKey(Group_, related_name="member_set")
            name = models.CharField(max_length=255, null=False, default="")

            class Meta:
                app_label = __name__

        cls.Group = Group_
        cls.Member = Member_

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

        group_dependencies = [node.to.model for node in walker[self.Group].dependencies]
        self.assertEqual(group_dependencies, [self.Member])

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

    def test_relation_fkname(self):
        walker = self._makeOne(self._get_models())
        walker.walkall()

        fkname = walker[self.Member].dependencies[0].fkname
        self.assertEqual(fkname, "group_id")


@test_target("django_mindscape:BidirectionalWalker")
class _ManyToManyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from django.db import models

        class Group_(models.Model):
            name = models.CharField(max_length=255, null=False, default="")

        class Meta:
            app_label = __name__ + "2"

        class Member_(models.Model):
            group_set = models.ManyToManyField(Group_, through="Group_ToMember_", related_name="member_set")
            name = models.CharField(max_length=255, null=False, default="")

            class Meta:
                app_label = __name__ + "2"

        class Group_ToMember_(models.Model):
            member = models.ForeignKey(Member_)
            group = models.ForeignKey(Group_)

            class Meta:
                app_label = __name__ + "2"

        cls.Group = Group_
        cls.Member = Member_
        cls.GroupToMember_ = Group_ToMember_

    def _get_models(self):
        return [self.Group, self.Member]

    def test_get_relation(self):
        walker = self._makeOne(self._get_models())
        walker.walkall()
        relations = walker[self.Member].dependencies
        self.assertNotEqual(len(relations), 0)

    def test_get_relation__reverse(self):
        walker = self._makeOne(self._get_models())
        walker.walkall()
        relations = walker[self.Group].dependencies
        self.assertNotEqual(len(relations), 0)

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
        self.assertEqual(through.model, self.GroupToMember_)

    def test_relation_fkname(self):
        walker = self._makeOne(self._get_models())
        walker.walkall()

        fkname = walker[self.Member].dependencies[0].fkname
        self.assertEqual(fkname, None)

    def test_relation_reverse_fkname(self):
        walker = self._makeOne(self._get_models())
        walker.walkall()

        fkname = walker[self.Group].dependencies[0].fkname
        self.assertEqual(fkname, None)


@test_target("django_mindscape:BidirectionalWalker")
class _OneToOneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from django.db import models

        class Group_(models.Model):
            name = models.CharField(max_length=255, null=False, default="")

            class Meta:
                app_label = "myapp3"

        class Member_(models.Model):
            group = models.OneToOneField(Group_, related_name="member")
            name = models.CharField(max_length=255, null=False, default="")

            class Meta:
                app_label = "myapp3"

        cls.Group = Group_
        cls.Member = Member_

    def _get_models(self):
        return [self.Group, self.Member]

    def test_relation(self):
        walker = self._makeOne(self._get_models())
        walker.walkall()

        self.assertNotEqual(len(walker[self.Member].dependencies), 0)

    def test_relation_reverse(self):
        walker = self._makeOne(self._get_models())
        walker.walkall()

        self.assertNotEqual(len(walker[self.Group].dependencies), 0)

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

    def test_relation_fkname(self):
        walker = self._makeOne(self._get_models())
        walker.walkall()

        fkname = walker[self.Member].dependencies[0].fkname
        self.assertEqual(fkname, "group_id")
