from django.db.models import CharField, IntegerField, Model, ForeignKey

from versions.models import Versionable, VersionedManyToManyField, VersionedForeignKey


def versionable_description(obj):
    return "<" + str(obj.__class__.__name__) + " object: " + str(
        obj.name) + " {valid: [" + obj.version_start_date.isoformat() + " | " + (
               obj.version_end_date.isoformat() if obj.version_end_date else "None") + "], created: " + obj.version_birth_date.isoformat() + "}>"


############################################
# The following model is used for:
# - CreationTest
# - DeletionTest
# - CurrentVersionTest
# - VersionedQuerySetTest
# - VersionNavigationTest
# - HistoricObjectsHandling
class B(Versionable):
    name = CharField(max_length=200)

    __str__ = versionable_description


############################################
# Models for
# - OneToManyTest
# - PrefetchingTest
class City(Versionable):
    name = CharField(max_length=200)

    __str__ = versionable_description


class Team(Versionable):
    name = CharField(max_length=200)
    city = VersionedForeignKey(City, null=True)

    __str__ = versionable_description


class Player(Versionable):
    name = CharField(max_length=200)
    team = VersionedForeignKey(Team, null=True)

    __str__ = versionable_description


class Award(Versionable):
    name = CharField(max_length=200)
    players = VersionedManyToManyField(Player, related_name='awards')


############################################
# SelfOneToManyTest models
class Directory(Versionable):
    name = CharField(max_length=100)
    parent = VersionedForeignKey('self', null=True)


# ############################################
# MultiM2MTest models
class Professor(Versionable):
    name = CharField(max_length=200)
    address = CharField(max_length=200)
    phone_number = CharField(max_length=200)

    __str__ = versionable_description


class Classroom(Versionable):
    name = CharField(max_length=200)
    building = CharField(max_length=200)

    __str__ = versionable_description


class Student(Versionable):
    name = CharField(max_length=200)
    professors = VersionedManyToManyField("Professor", related_name='students')
    classrooms = VersionedManyToManyField("Classroom", related_name='students')

    __str__ = versionable_description


############################################
# MultiM2MToSameTest models
class Pupil(Versionable):
    name = CharField(max_length=200)
    phone_number = CharField(max_length=200)
    language_teachers = VersionedManyToManyField('Teacher', related_name='language_students')
    science_teachers = VersionedManyToManyField('Teacher', related_name='science_students')

    __str__ = versionable_description


class Teacher(Versionable):
    name = CharField(max_length=200)
    domain = CharField(max_length=200)

    __str__ = versionable_description


############################################
# ManyToManyFilteringTest models
class C1(Versionable):
    name = CharField(max_length=50)
    c2s = VersionedManyToManyField("C2", related_name='c1s')

    __str__ = versionable_description


class C2(Versionable):
    name = CharField(max_length=50)
    c3s = VersionedManyToManyField("C3", related_name='c2s')

    __str__ = versionable_description


class C3(Versionable):
    name = CharField(max_length=50)

    __str__ = versionable_description


############################################
# HistoricM2MOperationsTests models
class Observer(Versionable):
    name = CharField(max_length=200)

    __str__ = versionable_description


class Subject(Versionable):
    name = CharField(max_length=200)
    observers = VersionedManyToManyField('Observer', related_name='subjects')

    __str__ = versionable_description


############################################
# VersionUniqueTests models
class ChainStore(Versionable):
    subchain_id = IntegerField()
    city = CharField(max_length=40)
    name = CharField(max_length=40)
    opening_hours = CharField(max_length=40)
    door_frame_color = VersionedForeignKey('Color')
    door_color = VersionedForeignKey('Color', related_name='cs')

    # There are lots of these chain stores.  They follow these rules:
    # - only one store with the same name and subchain_id can exist in a single city
    # - no two stores can share the same door_frame_color and door_color
    # Yea, well, they want to appeal to people who want to be different.
    VERSION_UNIQUE = [['subchain_id', 'city', 'name'], ['door_frame_color', 'door_color']]


class Color(Versionable):
    name = CharField(max_length=40)


############################################
# IntegrationNonVersionableModelsTests models
class Wine(Model):
    name = CharField(max_length=200)
    vintage = IntegerField()

    def __str__(self):
        return "<" + str(self.__class__.__name__) + " object: " + str(
            self.name) + " (" + str(self.vintage) + ")>"

class WineDrinker(Versionable):
    name = CharField(max_length=200)
    glass_content = ForeignKey(Wine, related_name='drinkers', null=True)

    __str__ = versionable_description

class WineDrinkerHat(Model):
    shape_choices = [('Sailor', 'Sailor'),
                     ('Cloche', 'Cloche'),
                     ('Cartwheel', 'Cartwheel'),
                     ('Turban', 'Turban'),
                     ('Breton', 'Breton'),
                     ('Vagabond', 'Vagabond')]
    color = CharField(max_length=40)
    shape = CharField(max_length=200, choices=shape_choices, default='Sailor')
    wearer = VersionedForeignKey(WineDrinker, related_name='hats', null=True)

    def __str__(self):
        return "<" + str(self.__class__.__name__) + " object: " + str(
            self.shape) + " (" + str(self.color) + ")>"


############################################
# SelfReferencingManyToManyTest models
class Person(Versionable):
    name = CharField(max_length=200)
    children = VersionedManyToManyField('self', symmetrical=False, null=True, related_name='parents')
