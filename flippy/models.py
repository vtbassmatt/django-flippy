from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from flippy.core import Feature


class FlippyFeature(models.Model):
    key = models.CharField(max_length=150, unique=True)
    boolean = models.BooleanField(null=True)
    percentage_of_actors = models.IntegerField(
        null=True,
        default=None,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ]
    )
    percentage_of_time = models.IntegerField(
        null=True,
        default=None,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ]
    )

    def __str__(self):
        return self.key
    
    def clear(self):
        self.boolean = None
        self.percentage_of_actors = None
        self.percentage_of_time = None
        self.save()
        self.enabled_actors.all().delete()
        self.enabled_groups.all().delete()
    
    def as_feature(self):
        f = Feature(self.key)
        f.boolean_gate.value = self.boolean
        f.actors_gate.value = [a.key for a in self.enabled_actors.all()]
        f.groups_gate.value = [g.key for g in self.enabled_groups.all()]
        f.percentage_of_actors_gate.value = self.percentage_of_actors
        f.percentage_of_time_gate.value = self.percentage_of_time
        return f
    
    @classmethod
    def from_feature(cls, feature: Feature):
        f = cls(key=feature.key)
        f.save()    # to get an ID assigned
        f.boolean = feature.boolean_gate.value
        for a in feature.actors_gate.value:
            f.enabled_actors.create(key=a)
        for g in feature.groups_gate.value:
            f.enabled_groups.create(key=g)
        f.percentage_of_actors = feature.percentage_of_actors_gate.value
        f.percentage_of_time = feature.percentage_of_time_gate.value
        f.save()
        return f


class FlippyActorGate(models.Model):
    key = models.CharField(max_length=150)
    feature = models.ForeignKey(
        FlippyFeature,
        on_delete=models.CASCADE,
        related_name='enabled_actors',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['key', 'feature'], name='actor_feature_uniq')
        ]
    
    def __str__(self):
        return self.key


class FlippyGroupGate(models.Model):
    key = models.CharField(max_length=150)
    feature = models.ForeignKey(
        FlippyFeature,
        on_delete=models.CASCADE,
        related_name='enabled_groups',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['key', 'feature'], name='group_feature_uniq')
        ]
    
    def __str__(self):
        return self.key
