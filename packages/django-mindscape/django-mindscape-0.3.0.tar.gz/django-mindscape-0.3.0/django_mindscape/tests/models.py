from django.db import models


class X(models.Model):
    pass


class Y(models.Model):
    xs = models.ManyToManyField(X, related_name="ys")


class Group(models.Model):
    name = models.CharField(max_length=255, null=False, default="")


class Grade(models.Model):
    group = models.ForeignKey(Group, null=True)
    name = models.CharField(max_length=255, null=False, default="")


class Member(models.Model):
    grade = models.ForeignKey(Grade)
    name = models.CharField(max_length=255, null=False, default="")
