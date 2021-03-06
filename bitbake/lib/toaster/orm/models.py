#
# ex:ts=4:sw=4:sts=4:et
# -*- tab-width: 4; c-basic-offset: 4; indent-tabs-mode: nil -*-
#
# BitBake Toaster Implementation
#
# Copyright (C) 2013        Intel Corporation
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from django.db import models
from django.utils.encoding import python_2_unicode_compatible


class Build(models.Model):
    SUCCEEDED = 0
    FAILED = 1
    IN_PROGRESS = 2

    BUILD_OUTCOME = (
        (SUCCEEDED, 'Succeeded'),
        (FAILED, 'Failed'),
        (IN_PROGRESS, 'In Progress'),
    )

    search_allowed_fields = ['machine', 'image_fstypes',
                             'cooker_log_path', "target__target"]

    machine = models.CharField(max_length=100)
    image_fstypes = models.CharField(max_length=100)
    distro = models.CharField(max_length=100)
    distro_version = models.CharField(max_length=100)
    started_on = models.DateTimeField()
    completed_on = models.DateTimeField()
    timespent = models.IntegerField(default=0)
    outcome = models.IntegerField(choices=BUILD_OUTCOME, default=IN_PROGRESS)
    errors_no = models.IntegerField(default=0)
    warnings_no = models.IntegerField(default=0)
    cooker_log_path = models.CharField(max_length=500)
    build_name = models.CharField(max_length=100)
    bitbake_version = models.CharField(max_length=50)

@python_2_unicode_compatible
class Target(models.Model):
    search_allowed_fields = ['target', 'image_fstypes', 'file_name']
    build = models.ForeignKey(Build)
    target = models.CharField(max_length=100)
    is_image = models.BooleanField(default = False)
    file_name = models.CharField(max_length=100)
    file_size = models.IntegerField()

    def __str__(self):
        return self.target



class TaskManager(models.Manager):
    def related_setscene(self, task_object):
        return Task.objects.filter(task_executed=True, build = task_object.build, recipe = task_object.recipe, task_name=task_object.task_name+"_setscene")

class Task(models.Model):

    SSTATE_NA = 0
    SSTATE_MISS = 1
    SSTATE_FAILED = 2
    SSTATE_RESTORED = 3

    SSTATE_RESULT = (
        (SSTATE_NA, 'Not Applicable'), # For rest of tasks, but they still need checking.
        (SSTATE_MISS, 'Missing'), # it is a miss
        (SSTATE_FAILED, 'Failed'), # there was a pkg, but the script failed
        (SSTATE_RESTORED, 'Restored'), # succesfully restored
    )

    CODING_NA = 0
    CODING_PYTHON = 2
    CODING_SHELL = 3

    TASK_CODING = (
        (CODING_NA, 'N/A'),
        (CODING_PYTHON, 'Python'),
        (CODING_SHELL, 'Shell'),
    )

    OUTCOME_SUCCESS = 0
    OUTCOME_COVERED = 1
    OUTCOME_CACHED = 2
    OUTCOME_PREBUILT = 3
    OUTCOME_FAILED = 4
    OUTCOME_NA = 5

    TASK_OUTCOME = (
        (OUTCOME_SUCCESS, 'Succeeded'),
        (OUTCOME_COVERED, 'Covered'),
        (OUTCOME_CACHED, 'Cached'),
        (OUTCOME_PREBUILT, 'Prebuilt'),
        (OUTCOME_FAILED, 'Failed'),
        (OUTCOME_NA, 'Not Available'),
    )

    search_allowed_fields = [ "recipe__name", "task_name" ]

    objects = TaskManager()

    def get_related_setscene(self):
        return Task.objects.related_setscene(self)

    build = models.ForeignKey(Build, related_name='task_build')
    order = models.IntegerField(null=True)
    task_executed = models.BooleanField(default=False) # True means Executed, False means Not/Executed
    outcome = models.IntegerField(choices=TASK_OUTCOME, default=OUTCOME_NA)
    sstate_checksum = models.CharField(max_length=100, blank=True)
    path_to_sstate_obj = models.FilePathField(max_length=500, blank=True)
    recipe = models.ForeignKey('Recipe', related_name='build_recipe')
    task_name = models.CharField(max_length=100)
    source_url = models.FilePathField(max_length=255, blank=True)
    work_directory = models.FilePathField(max_length=255, blank=True)
    script_type = models.IntegerField(choices=TASK_CODING, default=CODING_NA)
    line_number = models.IntegerField(default=0)
    disk_io = models.IntegerField(null=True)
    cpu_usage = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    elapsed_time = models.CharField(max_length=50, default=0)
    sstate_result = models.IntegerField(choices=SSTATE_RESULT, default=SSTATE_NA)
    message = models.CharField(max_length=240)
    logfile = models.FilePathField(max_length=255, blank=True)

    class Meta:
        ordering = ('order', 'recipe' ,)


class Task_Dependency(models.Model):
    task = models.ForeignKey(Task, related_name='task_dependencies_task')
    depends_on = models.ForeignKey(Task, related_name='task_dependencies_depends')

class Package(models.Model):
    search_allowed_fields = ['name', 'version', 'revision', 'recipe__name', 'recipe__version', 'recipe__license', 'recipe__layer_version__layer__name', 'recipe__layer_version__branch', 'recipe__layer_version__commit', 'recipe__layer_version__layer__local_path']
    build = models.ForeignKey('Build')
    recipe = models.ForeignKey('Recipe', null=True)
    name = models.CharField(max_length=100)
    installed_name = models.CharField(max_length=100, default='')
    version = models.CharField(max_length=100, blank=True)
    revision = models.CharField(max_length=32, blank=True)
    summary = models.CharField(max_length=200, blank=True)
    description = models.CharField(max_length=200, blank=True)
    size = models.IntegerField(default=0)
    installed_size = models.IntegerField(default=0)
    section = models.CharField(max_length=80, blank=True)
    license = models.CharField(max_length=80, blank=True)

class Package_Dependency(models.Model):
    TYPE_RDEPENDS = 0
    TYPE_TRDEPENDS = 1
    TYPE_RRECOMMENDS = 2
    TYPE_TRECOMMENDS = 3
    TYPE_RSUGGESTS = 4
    TYPE_RPROVIDES = 5
    TYPE_RREPLACES = 6
    TYPE_RCONFLICTS = 7
    ' TODO: bpackage should be changed to remove the DEPENDS_TYPE access '
    DEPENDS_TYPE = (
        (TYPE_RDEPENDS, "depends"),
        (TYPE_TRDEPENDS, "depends"),
        (TYPE_TRECOMMENDS, "recommends"),
        (TYPE_RRECOMMENDS, "recommends"),
        (TYPE_RSUGGESTS, "suggests"),
        (TYPE_RPROVIDES, "provides"),
        (TYPE_RREPLACES, "replaces"),
        (TYPE_RCONFLICTS, "conflicts"),
    )
    ''' Indexed by dep_type, in view order, key for short name and help
        description which when viewed will be printf'd with the
        package name.
    '''
    DEPENDS_DICT = {
        TYPE_RDEPENDS :     ("depends", "%s is required to run %s"),
        TYPE_TRDEPENDS :    ("depends", "%s is required to run %s"),
        TYPE_TRECOMMENDS :  ("recommends", "%s extends the usability of %s"),
        TYPE_RRECOMMENDS :  ("recommends", "%s extends the usability of %s"),
        TYPE_RSUGGESTS :    ("suggests", "%s is suggested for installation with %s"),
        TYPE_RPROVIDES :    ("provides", "%s is provided by %s"),
        TYPE_RREPLACES :    ("replaces", "%s is replaced by %s"),
        TYPE_RCONFLICTS :   ("conflicts", "%s conflicts with %s, which will not be installed if this package is not first removed"),
    }

    package = models.ForeignKey(Package, related_name='package_dependencies_source')
    depends_on = models.ForeignKey(Package, related_name='package_dependencies_target')   # soft dependency
    dep_type = models.IntegerField(choices=DEPENDS_TYPE)
    target = models.ForeignKey(Target, null=True)

class Target_Installed_Package(models.Model):
    target = models.ForeignKey(Target)
    package = models.ForeignKey(Package, related_name='buildtargetlist_package')

class Package_File(models.Model):
    package = models.ForeignKey(Package, related_name='buildfilelist_package')
    path = models.FilePathField(max_length=255, blank=True)
    size = models.IntegerField()

class Recipe(models.Model):
    search_allowed_fields = ['name', 'version', 'file_path', 'license', 'layer_version__layer__name', 'layer_version__branch', 'layer_version__commit', 'layer_version__layer__local_path']
    name = models.CharField(max_length=100, blank=True)
    version = models.CharField(max_length=100, blank=True)
    layer_version = models.ForeignKey('Layer_Version', related_name='recipe_layer_version')
    summary = models.CharField(max_length=100, blank=True)
    description = models.CharField(max_length=100, blank=True)
    section = models.CharField(max_length=100, blank=True)
    license = models.CharField(max_length=200, blank=True)
    licensing_info = models.TextField(blank=True)
    homepage = models.URLField(blank=True)
    bugtracker = models.URLField(blank=True)
    file_path = models.FilePathField(max_length=255)


class Recipe_Dependency(models.Model):
    TYPE_DEPENDS = 0
    TYPE_RDEPENDS = 1

    DEPENDS_TYPE = (
        (TYPE_DEPENDS, "depends"),
        (TYPE_RDEPENDS, "rdepends"),
    )
    recipe = models.ForeignKey(Recipe, related_name='r_dependencies_recipe')
    depends_on = models.ForeignKey(Recipe, related_name='r_dependencies_depends')
    dep_type = models.IntegerField(choices=DEPENDS_TYPE)

class Layer(models.Model):
    name = models.CharField(max_length=100)
    local_path = models.FilePathField(max_length=255)
    layer_index_url = models.URLField()


class Layer_Version(models.Model):
    build = models.ForeignKey(Build, related_name='layer_version_build')
    layer = models.ForeignKey(Layer, related_name='layer_version_layer')
    branch = models.CharField(max_length=50)
    commit = models.CharField(max_length=100)
    priority = models.IntegerField()


class Variable(models.Model):
    search_allowed_fields = ['variable_name', 'variable_value',
                             'vhistory__file_name', "description"]
    build = models.ForeignKey(Build, related_name='variable_build')
    variable_name = models.CharField(max_length=100)
    variable_value = models.TextField(blank=True)
    changed = models.BooleanField(default=False)
    human_readable_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

class VariableHistory(models.Model):
    variable = models.ForeignKey(Variable, related_name='vhistory')
    file_name = models.FilePathField(max_length=255)
    line_number = models.IntegerField(null=True)
    operation = models.CharField(max_length=16)

class LogMessage(models.Model):
    INFO = 0
    WARNING = 1
    ERROR = 2

    LOG_LEVEL = ( (INFO, "info"),
            (WARNING, "warn"),
            (ERROR, "error") )

    build = models.ForeignKey(Build)
    level = models.IntegerField(choices=LOG_LEVEL, default=INFO)
    message=models.CharField(max_length=240)
    pathname = models.FilePathField(max_length=255, blank=True)
    lineno = models.IntegerField(null=True)
