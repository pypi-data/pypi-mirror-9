import os
import posixpath
import logging

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.db.models.signals import post_save

from jukedj import validators

log = logging.getLogger(__name__)

# this could be solved by entry points to move these variables
# out of this app
GLOBAL_NAME = 'Global'
"""Name for global shots and sequences"""

RNDSEQ_NAME = 'RnD'
"""Name for the rnd sequence"""

DEFAULT_ASSETTYPES = [('prop', 'props that might be animated. props usually have a simple rig.'),
                      ('char', 'characters, that will be animated.'),
                      ('loc', 'locations and static objects.')]
"""Tuples with name and description for the default assettypes that should always be available."""

DEFAULT_DEPARTMENTS = [('Modeling', 'mod', 100, True),
                       ('Shading', 'shd', 200, True),
                       ('Rigging', 'rig', 300, True),
                       ('Animation', 'ani', 100, False),
                       ('Fx', 'fx', 200, False),
                       ('Lighting', 'lgt', 300, False),
                       ('Rendering', 'rdr', 400, False),
                       ('Compositing', 'comp', 500, False),
                       ('Grading', 'grd', 600, False)]
"""Tuples with name, short, ordervalue and assetflag for the default departments.
Every project will get these departments by default.
"""


class Project(models.Model):
    """Model for a project

    A project is at the top of the organisation hierarchy. All shots, assets etc belong to a certain project.
    When a project is created, :func:`muke.models.prj_post_save_handler` is executed.
    To make a project fully functional it needs at least a few entitys. the handler creates them automatically:

       1. create all default departments (for shots and assets). These are required, because we need them for example for handoff files.
       2. create all default assettypes. This will be \'char\', \'prop\' and \'loc\'.
       3. create all default sequences. Creates a global and a rnd sequence. The global squence contains a global shot where you can store project wide stuff, like caches, lightrigs etc.
          The rnd sequence has one shot for every user, where users can test, research and develop.

    The name of a project should only contain alphanumerical characters, spaces and underscores.
    The short of a project will be used in filenames and should only contain alphanumerical characters.

    """
    name = models.CharField(max_length=255, unique=True, validators=[validators.name_vld])
    short = models.CharField(max_length=10, unique=True, validators=[validators.alphanum_vld])
    _path = models.TextField(unique=True, verbose_name="path to project root")
    description = models.TextField(default="", blank=True)
    #thumbnail = models.ImageField(max_length=510, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    semester = models.CharField(max_length=50)
    framerate = models.FloatField(default=25)
    resx = models.IntegerField(verbose_name='horizontal resolution', default=1920)
    resy = models.IntegerField(verbose_name='vertical resolution', default=1080)
    scale = models.CharField(max_length=50, verbose_name='the maya scene scale', default='m')
    status = models.CharField(max_length=50, default='New')
    users = models.ManyToManyField(User, null=True, blank=True)

    @property
    def path(self):
        """Return path

        :returns: path
        :rtype: str
        :raises: None
        """
        p = os.path.normpath(self._path)
        if p.endswith(':'):
            p = p + os.path.sep
        return p

    @path.setter
    def path(self, value):
        """Set path

        :param value: The value for path
        :type value: str
        :raises: None
        """
        prepval = value.replace('\\', '/')
        self._path = posixpath.normpath(prepval)
        if self._path.endswith(':'):
            self._path = self._path + posixpath.sep

    @property
    def globalseq(self):
        """Return the global sequence

        :returns: the global sequence of the project
        :rtype: :class:`muke.models.Sequence`
        :raises: None
        """
        return self.sequence_set.get(name='Global')

    @property
    def rndseq(self):
        """Return the rnd sequence

        :returns: the rnd sequence of the project
        :rtype: :class:`muke.models.Sequence`
        :raises: None
        """
        return self.sequence_set.get(name='RnD')


class Atype(models.Model):
    """Model for an assettype.

    Assettypes group assets into categories. A assettype can belong to several projects. E.g. every project has a \'prop\' type.
    You can create new ones and projects. These projects then have a new asset category.
    """
    projects = models.ManyToManyField(Project, null=True, blank=True)
    name = models.CharField(max_length=255, unique=True, validators=[validators.alphanum_vld])
    description = models.TextField(default="", blank=True)
    #thumbnail = models.ImageField(max_length=510, null=True, blank=True)


class Sequence(models.Model):
    """Model for a sequence

    sequences group shots together. There are two special sequences in each project: \'Global\' and \'RnD\'.
    See :class:`muke.models.Project` for details
    """
    project = models.ForeignKey(Project)
    name = models.CharField(max_length=255, validators=[validators.alphanum_vld])
    description = models.TextField(default="", blank=True)
    #thumbnail = models.ImageField(max_length=510, null=True, blank=True)

    class Meta:
        unique_together=(("project", "name"))

    @property
    def globalshot(self):
        """Return the global shot

        :returns: the global shot of the sequence
        :rtype: :class:`muke.models.Shot`
        :raises: None
        """
        return self.shot_set.get(name='Global')


class Department(models.Model):
    """Model for a department

    A department describes what kind of work/data we handle. E.g. the shading department handles shaders.
    The modeling department handles models. There are a few default ones that should always be available.
    They get created with the first project.
    Projects can share departments. So there is only one modeling department.
    A department can either be for assets or for shots, depending on :meth:`muke.models.Department.assetflag`
    """
    projects = models.ManyToManyField(Project, null=True, blank=True)
    name = models.CharField(max_length=255, unique=True, validators=[validators.alphanum_vld])
    description = models.TextField(default="", blank=True)
    #thumbnail = models.ImageField(max_length=510, null=True, blank=True)
    short = models.CharField(max_length=10, unique=True, validators=[validators.alphanum_vld])
    ordervalue = models.IntegerField(default=0)
    assetflag = models.BooleanField(default=False)


class Task(models.Model):
    """Model for a task

    A task describes what kind of work (department) a set of users should do on a specific element (shot or asset).
    E.g. you create new tasks linked to the modeling department for asset \'wolf\'. If you add users to the task, these users
    know that they have to create the model of wolf.

    A task can be linked to either a shot or an asset.
    """
    project = models.ForeignKey(Project)
    department = models.ForeignKey(Department)
    #thumbnail = models.ImageField(max_length=510, null=True, blank=True)
    users = models.ManyToManyField(User, null=True, blank=True)
    status = models.CharField(max_length=50, default='New')
    deadline = models.DateField(null=True, blank=True)

    # link to asset or shot
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    element = GenericForeignKey()

    class Meta:
        unique_together= (("department", "content_type", "object_id"))
        ordering = ['department__ordervalue']

    @property
    def name(self):
        """Return department name

        :returns: name of the department
        :rtype: str
        :raises: None
        """
        return self.department.name

    @property
    def short(self):
        """Return department short

        :returns: short of the department
        :rtype: str
        :raises: None
        """
        return self.department.short


class Asset(models.Model):
    """Model for an asset

    On creation an asset gets a task assigned for each asset department that is connected to the project.
    """
    project = models.ForeignKey(Project)
    atype = models.ForeignKey(Atype, verbose_name="asset type")
    name = models.CharField(max_length=255, validators=[validators.alphanum_vld])
    description = models.TextField(default="", blank=True)
    tasks = GenericRelation(Task)
    #thumbnail = models.ImageField(max_length=510, null=True, blank=True)
    assets = models.ManyToManyField("self", symmetrical=False) # adds asset_set as related name

    class Meta:
        unique_together=(("project", "atype", "name"))


class Shot(models.Model):
    """Model for a shot

    there is one special shot in every sequence. It is the \'Global\' shot. In the \'RnD\' sequence,
    every user has its own shot.
    On creation a shot gets a task assigned for each shot department that is connected to the project.
    """
    project = models.ForeignKey(Project)
    sequence = models.ForeignKey(Sequence)
    name = models.CharField(max_length=255, validators=[validators.alphanum_vld])
    description = models.TextField(default="", blank=True)
    #thumbnail = models.ImageField(max_length=510, null=True, blank=True)
    tasks = GenericRelation(Task)
    assets = models.ManyToManyField(Asset, null=True, blank=True)
    startframe = models.IntegerField(default=1001)
    endframe = models.IntegerField(default=1050)
    handlesize = models.IntegerField(default=8)

    class Meta:
        unique_together = (("project", "sequence", "name"))

    @property
    def duration(self):
        """Return the duration

        :returns: duration of the shot in frames
        :rtype: int
        :raises: None
        """
        return self.endframe - self.startframe + 1

    def clean(self, ):
        """Reimplemented from :class:`models.Model`. Check if startframe is before endframe

        :returns: None
        :rtype: None
        :raises: ValidationError
        """
        if self.startframe > self.endframe:
            raise ValidationError("Shot starts before it ends: Framerange(%s - %s)" % (self.startframe, self.endframe))


class Software(models.Model):
    """Model for a software e.g. Maya that can store a thumbnail etc"""
    name = models.CharField(max_length=100, unique=True, validators=[validators.name_vld])
    #thumbnail = models.ImageField(max_length=510, null=True, blank=True)


class Note(models.Model):
    """Model for comments to objects
    """
    # link an object
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    parent = GenericForeignKey('content_type', 'object_id')
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now_add=True, auto_now=True)
    user = models.ForeignKey(User)
    content = models.TextField(default="", blank=True)


class File(models.Model):
    """Model for a general file that is stored somewhere on a disk"""

    user = models.ForeignKey(User)
    _path = models.TextField(unique=True, verbose_name="the filepath to the file on some harddrive")
    software = models.ForeignKey(Software, null=True, blank=True)
    isopen = models.BooleanField(default=False)
    #thumbnail = models.ImageField(max_length=510, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now_add=True, auto_now=True)
    notes = GenericRelation(Note)

    @property
    def path(self):
        """Return path

        :returns: path
        :rtype: str
        :raises: None
        """
        return os.path.normpath(self._path)

    @path.setter
    def path(self, value):
        """Set path

        :param value: The value for path
        :type value: str
        :raises: None
        """
        prepval = value.replace('\\', '/')
        self._path = posixpath.normpath(prepval)

    @property
    def filename(self):
        """Return filename

        :returns: the filename without the path
        :rtype: str
        :raises: None
        """
        return os.path.basename(self.path)

    @property
    def ext(self):
        """Return the extension of the file

        :returns: the extension with the extension seperator, e.g ``.mb`` or an empty string if there is no extension
        :rtype: str
        :raises: None
        """
        return os.path.splitext(self.path)[1]


class TaskFile(File):
    """Model for a file that belongs to a specific task"""
    task = models.ForeignKey(Task)
    version = models.IntegerField(default=1)
    releasetype = models.CharField(max_length=20)
    descriptor = models.TextField(null=True, blank=True)
    typ = models.TextField(default=None)

    class Meta:
        unique_together = (('task', 'releasetype', 'version', 'descriptor', 'typ'))


def add_default_deps(project):
    """Add or create the default departments for the given project

    :param project: the project that needs default departments
    :type project: :class:`muke.models.Project`
    :returns: None
    :rtype: None
    :raises: None
    """
    # create deps for project
    for name, short, order, af in DEFAULT_DEPARTMENTS:
        dep, created = Department.objects.get_or_create(name=name, short=short, ordervalue=order, assetflag=af)
        dep.projects.add(project)
        dep.full_clean()
        dep.save()


def add_default_atypes(project):
    """Add or create the default assettypes for the given project

    :param project: the project that needs default assettypes
    :type project: :class:`muke.models.Project`
    :returns: None
    :rtype: None
    :raises: None
    """
    # create assettypes for project
    for name, desc in DEFAULT_ASSETTYPES:
        at, created = Atype.objects.get_or_create(name=name, defaults={'description': desc})
        at.projects.add(project)
        at.full_clean()
        at.save()


def add_default_sequences(project):
    """Add or create the default sequences for the given project

    :param project: the project that needs default sequences
    :type project: :class:`muke.models.Project`
    :returns: None
    :rtype: None
    :raises: None
    """
    # create sequences for project
    seqs = [(GLOBAL_NAME, 'global sequence for project %s' % project.name),
            (RNDSEQ_NAME, 'research and development sequence for project %s' % project.name)]
    for name, desc in seqs:
        seq, created = Sequence.objects.get_or_create(name=name, project=project, defaults={'description': desc})


def add_userrnd_shot(project):
    """Add a rnd shot for every user in the project

    :param project: the project that needs its rnd shots updated
    :type project: :class:`muke.models.Project`
    :returns: None
    :rtype: None
    :raises: None
    """
    rndseq = project.sequence_set.get(name=RNDSEQ_NAME)
    users = [u for u in project.users.all()]
    for user in users:
        shot, created = Shot.objects.get_or_create(name=user.username,
                                                   project=project,
                                                   sequence=rndseq,
                                                   defaults={'description': 'rnd shot for user %s' % user.username})
        for t in shot.tasks.all():
            t.users.add(user)
            t.full_clean()
            t.save()


@receiver(post_save, sender=Project)
def prj_post_save_handler(sender, **kwargs):
    """ Post save receiver for when a Project is saved.

    Creates a rnd shot for every user.

    On creations does:

       1. create all default departments
       2. create all default assettypes
       3. create all default sequences

    :param sender: the project class
    :type sender: :class:`muke.models.Project`
    :returns:  None
    :raises: None

    """
    prj = kwargs['instance']
    if not kwargs['created']:
        add_userrnd_shot(prj)
        return

    add_default_deps(prj)
    add_default_atypes(prj)
    add_default_sequences(prj)


@receiver(post_save, sender=Sequence)
def seq_post_save_handler(sender, **kwargs):
    """ Post save receiver for when a sequence is saved.

    creates a global shot.

    :param sender: the sequence class
    :type sender: :class:`muke.models.Sequence`
    :returns:  None
    :raises: None

    """
    if not kwargs['created']:
        return
    seq = kwargs['instance']
    if seq.name == RNDSEQ_NAME:
        return

    prj = seq.project
    name = GLOBAL_NAME
    desc = "Global shot for sequence %s" % seq.name
    Shot.objects.create(name=name, project=prj, sequence=seq, description=desc)


def create_all_tasks(element):
    """Create all tasks for the element

    :param element: The shot or asset that needs tasks
    :type element: :class:`muke.models.Shot` | :class:`muke.models.Asset`
    :returns: None
    :rtype: None
    :raises: None
    """
    prj = element.project
    if isinstance(element, Asset):
        flag=True
    else:
        flag=False
    deps = prj.department_set.filter(assetflag=flag)
    for d in deps:
        t = Task(project=prj, department=d, element=element)
        t.full_clean()
        t.save()


@receiver(post_save, sender=Shot)
def shot_post_save_handler(sender, **kwargs):
    """ Post save receiver for when a shot is saved.

    :param sender: the shot class
    :type sender: :class:`muke.models.Shot`
    :returns:  None
    :raises: None

    """
    if not kwargs['created']:
        return
    shot = kwargs['instance']
    create_all_tasks(shot)


@receiver(post_save, sender=Asset)
def asset_post_save_handler(sender, **kwargs):
    """ Post save receiver for when a asset is saved.

    :param sender: the asset class
    :type sender: :class:`muke.models.Asset`
    :returns:  None
    :raises: None

    """
    if not kwargs['created']:
        return
    asset = kwargs['instance']
    create_all_tasks(asset)
