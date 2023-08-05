#!/usr/bin/env python
import requests
import webbrowser
import xml.etree.ElementTree as ET
import argparse
import sys
import hashlib
import subprocess
from xml.dom.minidom import parseString
from xml.sax.saxutils import escape


def prettify(xml_string):
    xml = parseString(xml_string)
    formatted_but_with_blank_lines = xml.toprettyxml()
    non_blank_lines = [l for l in formatted_but_with_blank_lines.split('\n') if len(l.strip()) != 0]
    return '\n'.join(non_blank_lines)


class CommonEqualityMixin(object):
    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(str(self))

    def __repr__(self):
        keys = self.__dict__.keys()
        keys.sort()
        return "Some %s" % self.__class__ + " Fields[" + (
            ", ".join([str(k) + ":" + str(self.__dict__[k]) for k in keys]) + "]")


class Ensurance:
    def __init__(self, element):
        self._element = element

    def ensure_child(self, name):
        child = self._element.find(name)
        if child is None:
            result = ET.fromstring('<%s></%s>' % (name, name))
            self._element.append(result)
            return Ensurance(result)
        else:
            return Ensurance(child)

    def ensure_child_with_attribute(self, name, attribute_name, attribute_value):
        matching_elements = [e for e in self._element.findall(name) if e.attrib[attribute_name] == attribute_value]
        if len(matching_elements) == 0:
            new_element = ET.fromstring('<%s %s="%s"></%s>' % (name, attribute_name, attribute_value, name))
            self._element.append(new_element)
            return Ensurance(new_element)
        else:
            return Ensurance(matching_elements[0])

    def set(self, attribute_name, value):
        self._element.set(attribute_name, value)
        return self

    def append(self, element):
        self._element.append(element)
        return element

    def set_text(self, value):
        self._element.text = value


class PossiblyMissingElement:
    def __init__(self, element):
        self.element = element

    def possibly_missing_child(self, name):
        if self.element is None:
            return PossiblyMissingElement(None)
        else:
            return PossiblyMissingElement(self.element.find(name))

    def findall(self, name):
        if self.element is None:
            return []
        else:
            return self.element.findall(name)

    def iterator(self):
        if self.element is None:
            return []
        else:
            return self.element

    def has_attribute(self, name, value):
        if self.element is None:
            return False
        else:
            return name in self.element.attrib and self.element.attrib[name] == value

    def remove_all_children(self, tag_name_to_remove=None):
        children = []
        if self.element is not None:
            for child in self.element:
                if tag_name_to_remove is None or child.tag == tag_name_to_remove:
                    children.append(child)

        for child in children:
            self.element.remove(child)

        return self

    def remove_attribute(self, attribute_name):
        if self.element is not None:
            if attribute_name in self.element.attrib:
                del self.element.attrib[attribute_name]

        return self


class ThingWithResources(CommonEqualityMixin):
    def __init__(self, element):
        self.element = element

    def resources(self):
        return set([e.text for e in PossiblyMissingElement(self.element).possibly_missing_child('resources').findall('resource')])

    def ensure_resource(self, resource):
        if resource not in self.resources():
            Ensurance(self.element).ensure_child('resources').append(ET.fromstring('<resource>%s</resource>' % resource))


class ThingWithEnvironmentVariables:
    def __init__(self, element):
        self.element = element

    def _is_encrypted(self, variable_element):
        return 'secure' in variable_element.attrib and variable_element.attrib['secure'] == 'true'

    def _environment_variables(self, encrypted):
        variable_elements = PossiblyMissingElement(self.element).possibly_missing_child("environmentvariables").findall("variable")
        result = {}
        for variable_element in variable_elements:
            if encrypted == self._is_encrypted(variable_element):
                if encrypted:
                    value_attribute = "encryptedValue"
                else:
                    value_attribute = "value"
                result[variable_element.attrib['name']] = variable_element.find(value_attribute).text
        return result

    def environment_variables(self):
        return self._environment_variables(False)

    def encrypted_environment_variables(self):
        return self._environment_variables(True)

    def _ensure_environment_variables(self, environment_variables, encrypted):
        environment_variables_ensurance = Ensurance(self.element).ensure_child("environmentvariables")
        for key, value in environment_variables.iteritems():
            variable_element = environment_variables_ensurance.ensure_child_with_attribute("variable", "name", key)
            if encrypted:
                value_element = variable_element.set("secure", "true").ensure_child("encryptedValue")
            else:
                value_element = variable_element.ensure_child("value")
            value_element.set_text(value)

    def ensure_environment_variables(self, environment_variables):
        self._ensure_environment_variables(environment_variables, False)

    def ensure_encrypted_environment_variables(self, environment_variables):
        self._ensure_environment_variables(environment_variables, True)

    def remove_all(self):
        PossiblyMissingElement(self.element).possibly_missing_child("environmentvariables").remove_all_children()

    def as_python(self):
        result = ""
        environment_variables = self.environment_variables()
        if environment_variables:
            result += '.ensure_environment_variables(%s)' % environment_variables
        encrypted_environment_variables = self.encrypted_environment_variables()
        if encrypted_environment_variables:
            result += '.ensure_encrypted_environment_variables(%s)' % encrypted_environment_variables
        return result


def move_all_to_end(parent_element, tag):
    elements = parent_element.findall(tag)
    for element in elements:
        parent_element.remove(element)
        parent_element.append(element)

def runifFrom(element):
    runifs = [e.attrib['status'] for e in element.findall("runif")]
    if len(runifs) == 0:
        return 'passed'
    if len(runifs) == 1:
        return runifs[0]
    if len(runifs) == 2 and 'passed' in runifs and 'failed' in runifs:
        return 'any'
    raise RuntimeError("Don't know what multiple runif values (%s) means" % runifs)

def Task(element):
    runif = runifFrom(element)
    if element.tag == "exec":
        command_and_args = [element.attrib["command"]] + [e.text for e in element.findall('arg')]
        working_dir = element.attrib.get("workingdir", None)  # TODO not ideal to return "None" for working_dir
        return ExecTask(command_and_args, working_dir, runif)
    if element.tag == "fetchartifact":
        dest = element.attrib.get('dest', None)
        return FetchArtifactTask(element.attrib['pipeline'], element.attrib['stage'], element.attrib['job'], fetch_artifact_src_from(element), dest, runif)
    if element.tag == "rake":
        return RakeTask(element.attrib['target'])
    raise RuntimeError("Don't know task type %s" % element.tag)


class AbstractTask(CommonEqualityMixin):
    def __init__(self, runif):
        self._runif = runif
        valid_values = ['passed', 'failed', 'any']
        if runif not in valid_values:
            raise RuntimeError('Cannot create task with runif="%s" - it must be one of %s' % (runif, valid_values))

    def runif(self):
        return self._runif


def fetch_artifact_src_from(element):
    if 'srcfile' in element.attrib:
        return FetchArtifactFile(element.attrib['srcfile'])
    if 'srcdir' in element.attrib:
        return FetchArtifactDir(element.attrib['srcdir'])
    raise RuntimeError("Expected srcfile or srcdir. Do not know what src type to use for " + ET.tostring(element, 'utf-8'))


class FetchArtifactFile(CommonEqualityMixin):
    def __init__(self, src_value):
        self.src_value = src_value

    def __repr__(self):
        return 'FetchArtifactFile("%s")' % self.src_value

    def as_xml_type_and_value(self):
        return "srcfile", self.src_value


class FetchArtifactDir(CommonEqualityMixin):
    def __init__(self, src_value):
        self.src_value = src_value

    def __repr__(self):
        return 'FetchArtifactDir("%s")' % self.src_value

    def as_xml_type_and_value(self):
        return "srcdir", self.src_value


class FetchArtifactTask(AbstractTask):
    def __init__(self, pipeline, stage, job, src, dest=None, runif="passed"):
        super(self.__class__, self).__init__(runif)
        self._pipeline = pipeline
        self._stage = stage
        self._job = job
        self._src = src
        self._dest = dest

    def __repr__(self):
        dest_parameter = ""
        if self._dest is not None:
            dest_parameter = ', dest="%s"' % self._dest

        runif_parameter = ""
        if self._runif != "passed":
            runif_parameter = ', runif="%s"' % self._runif

        return ('FetchArtifactTask("%s", "%s", "%s", %s' % (self._pipeline, self._stage, self._job, self._src)) + dest_parameter + runif_parameter + ')'

    def type(self):
        return "fetchartifact"

    def pipeline(self):
        return self._pipeline

    def stage(self):
        return self._stage

    def job(self):
        return self._job

    def src(self):
        return self._src

    def dest(self):
        return self._dest

    def append_to(self, element):
        src_type, src_value = self.src().as_xml_type_and_value()
        if self._dest is None:
            new_element = ET.fromstring(
                '<fetchartifact pipeline="%s" stage="%s" job="%s" %s="%s" />' % (self._pipeline, self._stage, self._job, src_type, src_value))
        else:
            new_element = ET.fromstring(
                '<fetchartifact pipeline="%s" stage="%s" job="%s" %s="%s" dest="%s"/>' % (
                    self._pipeline, self._stage, self._job, src_type, src_value, self._dest))
        new_element.append(ET.fromstring('<runif status="%s" />' % self.runif()))

        Ensurance(element).ensure_child("tasks").append(new_element)
        return Task(new_element)


class ExecTask(AbstractTask):
    def __init__(self, command_and_args, working_dir=None, runif="passed"):
        super(self.__class__, self).__init__(runif)
        self._command_and_args = command_and_args
        self._working_dir = working_dir

    def __repr__(self):
        working_dir_parameter = ""
        if self._working_dir is not None:
            working_dir_parameter = ', working_dir="%s"' % self._working_dir

        runif_parameter = ""
        if self._runif != "passed":
            runif_parameter = ', runif="%s"' % self._runif

        return ('ExecTask(%s' % self.command_and_args()) + working_dir_parameter + runif_parameter + ')'

    def type(self):
        return "exec"

    def command_and_args(self):
        return self._command_and_args

    def working_dir(self):
        return self._working_dir

    def append_to(self, element):
        if self._working_dir is None:
            new_element = ET.fromstring('<exec command="%s"></exec>' % self._command_and_args[0])
        else:
            new_element = ET.fromstring('<exec command="%s" workingdir="%s"></exec>' % (self._command_and_args[0], self._working_dir))

        for arg in self._command_and_args[1:]:
            new_element.append(ET.fromstring('<arg>%s</arg>' % escape(arg)))

        new_element.append(ET.fromstring('<runif status="%s" />' % self.runif()))

        Ensurance(element).ensure_child("tasks").append(new_element)
        return Task(new_element)


class RakeTask(AbstractTask):
    def __init__(self, target, runif="passed"):
        super(self.__class__, self).__init__(runif)
        self._target = target

    def __repr__(self):
        return 'RakeTask("%s", "%s")' % (self._target, self._runif)

    def type(self):
        return "rake"

    def target(self):
        return self._target

    def append_to(self, element):
        new_element = ET.fromstring('<rake target="%s"></rake>' % self._target)
        Ensurance(element).ensure_child("tasks").append(new_element)
        return Task(new_element)


def ArtifactFor(element):
    dest = element.attrib.get('dest', None)
    return Artifact(element.tag, element.attrib['src'], dest)


def BuildArtifact(src, dest=None):
    return Artifact("artifact", src, dest)


def TestArtifact(src, dest=None):
    return Artifact("test", src, dest)


class Artifact(CommonEqualityMixin):
    def __init__(self, tag, src, dest=None):
        self.tag = tag
        self.src = src
        self.dest = dest

    def __repr__(self):
        if self.dest is None:
            return '%s("%s")' % (self.constructor(), self.src)
        else:
            return '%s("%s", "%s")' % (self.constructor(), self.src, self.dest)

    def append_to(self, element):
        if self.dest is None:
            element.append(ET.fromstring('<%s src="%s" />' % (self.tag, self.src)))
        else:
            element.append(ET.fromstring('<%s src="%s" dest="%s" />' % (self.tag, self.src, self.dest)))

    def constructor(self):
        if self.tag == "artifact":
            return "BuildArtifact"
        if self.tag == "test":
            return "TestArtifact"
        raise RuntimeError("Unknown artifact tag %s" % self.tag)


class Tab(CommonEqualityMixin):
    def __init__(self, name, path):
        self.name = name
        self.path = path

    def __repr__(self):
        return 'Tab("%s", "%s")' % (self.name, self.path)

    def append_to(self, element):
        element.append(ET.fromstring('<tab name="%s" path="%s" />' % (self.name, self.path)))


class Job(CommonEqualityMixin):
    def __init__(self, element):
        self.element = element
        self.thing_with_resources = ThingWithResources(element)

    def name(self):
        return self.element.attrib['name']

    def has_timeout(self):
        return 'timeout' in self.element.attrib

    def timeout(self):
        if not self.has_timeout():
            raise RuntimeError("Job (%s) does not have timeout" % self)
        return self.element.attrib['timeout']

    def set_timeout(self, timeout):
        self.element.attrib['timeout'] = timeout
        return self

    def runs_on_all_agents(self):
        return self.element.attrib.get('runOnAllAgents', 'false') == 'true'

    def set_runs_on_all_agents(self):
        self.element.attrib['runOnAllAgents'] = 'true'
        return self

    def resources(self):
        return self.thing_with_resources.resources()

    def ensure_resource(self, resource):
        self.thing_with_resources.ensure_resource(resource)
        return self

    def artifacts(self):
        artifact_elements = PossiblyMissingElement(self.element).possibly_missing_child("artifacts").iterator()
        return set([ArtifactFor(e) for e in artifact_elements])

    def ensure_artifacts(self, artifacts):
        artifacts_ensurance = Ensurance(self.element).ensure_child("artifacts")
        artifacts_to_add = artifacts.difference(self.artifacts())
        for artifact in artifacts_to_add:
            artifact.append_to(artifacts_ensurance)
        return self

    def tabs(self):
        return [Tab(e.attrib['name'], e.attrib['path']) for e in PossiblyMissingElement(self.element).possibly_missing_child('tabs').findall('tab')]

    def ensure_tab(self, tab):
        tab_ensurance = Ensurance(self.element).ensure_child("tabs")
        if self.tabs().count(tab) == 0:
            tab.append_to(tab_ensurance)
        return self

    def tasks(self):
        return [Task(e) for e in PossiblyMissingElement(self.element).possibly_missing_child("tasks").iterator()]

    def add_task(self, task):
        return task.append_to(self.element)

    def ensure_task(self, task):
        if self.tasks().count(task) == 0:
            return task.append_to(self.element)
        else:
            return task

    def without_any_tasks(self):
        PossiblyMissingElement(self.element).possibly_missing_child("tasks").remove_all_children()
        return self

    def environment_variables(self):
        return ThingWithEnvironmentVariables(self.element).environment_variables()

    def ensure_environment_variables(self, environment_variables):
        ThingWithEnvironmentVariables(self.element).ensure_environment_variables(environment_variables)
        return self

    def without_any_environment_variables(self):
        ThingWithEnvironmentVariables(self.element).remove_all()
        return self

    def reorder_elements_to_please_go(self):
        move_all_to_end(self.element, "environment_variables")
        move_all_to_end(self.element, "tasks")
        move_all_to_end(self.element, "tabs")
        move_all_to_end(self.element, "resources")
        move_all_to_end(self.element, "artifacts")

    def as_python_commands_applied_to_stage(self):
        result = 'job = stage.ensure_job("%s")' % self.name()

        if self.artifacts():
            if len(self.artifacts()) > 1:
                artifacts_sorted = list(self.artifacts())
                artifacts_sorted.sort(key=lambda artifact: str(artifact))
                result += '.ensure_artifacts(set(%s))' % artifacts_sorted
            else:
                result += '.ensure_artifacts({%s})' % self.artifacts().pop()

        result += ThingWithEnvironmentVariables(self.element).as_python()

        for resource in self.resources():
            result += '.ensure_resource("%s")' % resource

        for tab in self.tabs():
            result += '.ensure_tab(%s)' % tab

        if self.has_timeout():
            result += '.set_timeout("%s")' % self.timeout()

        if self.runs_on_all_agents():
            result += '.set_runs_on_all_agents()'

        for task in self.tasks():
            # we add instead of ensure because we know it is starting off empty and need to handle duplicate tasks
            result += "\njob.add_task(%s)" % task

        return result


class Stage(CommonEqualityMixin):
    def __init__(self, element):
        self.element = element

    def __repr__(self):
        return 'Stage(%s)' % self.name()

    def name(self):
        return self.element.attrib['name']

    def jobs(self):
        return [Job(job_element) for job_element in PossiblyMissingElement(self.element).possibly_missing_child('jobs').findall('job')]

    def ensure_job(self, name):
        job_element = Ensurance(self.element).ensure_child("jobs").ensure_child_with_attribute("job", "name", name)
        return Job(job_element._element)

    def environment_variables(self):
        return ThingWithEnvironmentVariables(self.element).environment_variables()

    def ensure_environment_variables(self, environment_variables):
        ThingWithEnvironmentVariables(self.element).ensure_environment_variables(environment_variables)
        return self

    def without_any_environment_variables(self):
        ThingWithEnvironmentVariables(self.element).remove_all()
        return self

    def set_clean_working_dir(self):
        self.element.attrib['cleanWorkingDir'] = "true"
        return self

    def clean_working_dir(self):
        return PossiblyMissingElement(self.element).has_attribute('cleanWorkingDir', "true")

    def has_manual_approval(self):
        return PossiblyMissingElement(self.element).possibly_missing_child("approval").has_attribute("type", "manual")

    def fetch_materials(self):
        return not PossiblyMissingElement(self.element).has_attribute("fetchMaterials", "false")

    def set_fetch_materials(self, value):
        if value:
            PossiblyMissingElement(self.element).remove_attribute("fetchMaterials")
        else:
            Ensurance(self.element).set("fetchMaterials", "false")
        return self

    def set_has_manual_approval(self):
        Ensurance(self.element).ensure_child_with_attribute("approval", "type", "manual")
        return self

    def reorder_elements_to_please_go(self):
        move_all_to_end(self.element, "environmentvariables")
        move_all_to_end(self.element, "jobs")

        for job in self.jobs():
            job.reorder_elements_to_please_go()

    def as_python_commands_applied_to_pipeline(self):
        result = 'stage = pipeline.ensure_stage("%s")' % self.name()

        result += ThingWithEnvironmentVariables(self.element).as_python()

        if self.clean_working_dir():
            result += '.set_clean_working_dir()'

        if self.has_manual_approval():
            result += '.set_has_manual_approval()'

        if not self.fetch_materials():
            result += '.set_fetch_materials(False)'

        for job in self.jobs():
            result += '\n%s' % job.as_python_commands_applied_to_stage()

        return result


def ignore_patterns_in(element):
    return set([e.attrib['pattern'] for e in PossiblyMissingElement(element).possibly_missing_child("filter").findall("ignore")])


def Materials(element):
    if element.tag == "git":
        branch = element.attrib.get('branch', None)
        material_name = element.attrib.get('materialName', None)
        polling = element.attrib.get('autoUpdate', 'true') == 'true'
        return GitMaterial(element.attrib['url'], branch, material_name, polling, ignore_patterns_in(element))
    if element.tag == "pipeline":
        material_name = element.attrib.get('materialName', None)
        return PipelineMaterial(element.attrib['pipelineName'], element.attrib['stageName'], material_name)
    raise RuntimeError("don't know of material matching " + ET.tostring(element, 'utf-8'))


class GitMaterial(CommonEqualityMixin):
    def __init__(self, url, branch=None, material_name=None, polling=True, ignore_patterns=set()):
        self._url = url
        self._branch = branch
        self._material_name = material_name
        self._polling = polling
        self._ignore_patterns = ignore_patterns

    def __repr__(self):
        branch_part = ""
        if not self.is_on_master():
            branch_part = ', branch="%s"' % self._branch
        material_name_part = ""
        if self._material_name is not None:
            material_name_part = ', material_name="%s"' % self._material_name
        polling_part = ''
        if not self._polling:
            polling_part = ', polling=False'
        ignore_patterns_part = ''
        if self.ignore_patterns():
            ignore_patterns_part = ', ignore_patterns=%s' % self.ignore_patterns()
        return ('GitMaterial("%s"' % self._url) + branch_part + material_name_part + polling_part + ignore_patterns_part + ')'

    def _has_options(self):
        return (not self.is_on_master()) or (self._material_name is not None) or (not self._polling)

    def is_on_master(self):
        return self._branch is None or self._branch == 'master'

    def as_python_applied_to_pipeline(self):
        if self._has_options():
            return 'set_git_material(%s)' % str(self)
        else:
            return 'set_git_url("%s")' % self._url

    def is_git(self):
        return True

    def url(self):
        return self._url

    def polling(self):
        return self._polling

    def branch(self):
        if self.is_on_master():
            return 'master'
        else:
            return self._branch

    def material_name(self):
        return self._material_name

    def ignore_patterns(self):
        return self._ignore_patterns

    def append_to(self, element):
        branch_part = ""
        if not self.is_on_master():
            branch_part = ' branch="%s"' % self._branch
        material_name_part = ""
        if self._material_name is not None:
            material_name_part = ' materialName="%s"' % self._material_name
        polling_part = ''
        if not self._polling:
            polling_part = ' autoUpdate="false"'
        new_element = ET.fromstring(('<git url="%s"' % self._url) + branch_part + material_name_part + polling_part + ' />')
        if self.ignore_patterns():
            filter_element = ET.fromstring("<filter/>")
            new_element.append(filter_element)
            for ignore_pattern in self.ignore_patterns():
                filter_element.append(ET.fromstring('<ignore pattern="%s"/>' % ignore_pattern))
        element.append(new_element)


class PipelineMaterial(CommonEqualityMixin):
    def __init__(self, pipeline_name, stage_name, material_name=None):
        self._pipeline_name = pipeline_name
        self._stage_name = stage_name
        self._material_name = material_name

    def __repr__(self):
        if self._material_name is None:
            return 'PipelineMaterial("%s", "%s")' % (self._pipeline_name, self._stage_name)
        else:
            return 'PipelineMaterial("%s", "%s", "%s")' % (self._pipeline_name, self._stage_name, self._material_name)

    def is_git(self):
        return False

    def append_to(self, element):
        if self._material_name is None:
            new_element = ET.fromstring('<pipeline pipelineName="%s" stageName="%s" />' % (self._pipeline_name, self._stage_name))
        else:
            new_element = ET.fromstring(
                '<pipeline pipelineName="%s" stageName="%s" materialName="%s"/>' % (self._pipeline_name, self._stage_name, self._material_name))

        element.append(new_element)


class Pipeline(CommonEqualityMixin):
    def __init__(self, element, parent):
        self.parent = parent
        self.element = element

    def name(self):
        return self.element.attrib['name']

    def as_python_commands_applied_to_server(self):
        def then(s):
            return '\\\n\t.' + s

        result = (
                     then('ensure_pipeline_group("%s")') +
                     then('ensure_replacement_of_pipeline("%s")')
                 ) % (self.parent.name(), self.name())

        if self.has_timer():
            result += then('set_timer("%s")' % self.timer())

        if self.has_label_template():
            if self.label_template() == DEFAULT_LABEL_TEMPLATE:
                result += then('set_default_label_template()')
            else:
                result += then('set_label_template("%s")' % self.label_template())

        if self.has_automatic_pipeline_locking():
            result += then('set_automatic_pipeline_locking()')

        if self.has_single_git_material():
            result += then(self.git_material().as_python_applied_to_pipeline())

        for material in self.materials():
            if not (self.has_single_git_material() and material.is_git()):
                result += then('ensure_material(%s)' % material)

        result += ThingWithEnvironmentVariables(self.element).as_python()

        if len(self.parameters()) != 0:
            result += then('ensure_parameters(%s)' % self.parameters())

        for stage in self.stages():
            result += "\n" + stage.as_python_commands_applied_to_pipeline()

        return result

    def __repr__(self):
        return 'Pipeline("%s", "%s")' % (self.name(), self.parent)

    def has_label_template(self):
        return 'labeltemplate' in self.element.attrib

    def set_automatic_pipeline_locking(self):
        self.element.attrib['isLocked'] = 'true'
        return self

    def has_automatic_pipeline_locking(self):
        return 'isLocked' in self.element.attrib and self.element.attrib['isLocked'] == 'true'

    def label_template(self):
        return self.element.attrib['labeltemplate']

    def set_label_template(self, label_template):
        self.element.attrib['labeltemplate'] = label_template
        return self

    def set_default_label_template(self):
        return self.set_label_template(DEFAULT_LABEL_TEMPLATE)

    def materials(self):
        return [Materials(element) for element in PossiblyMissingElement(self.element).possibly_missing_child('materials').iterator()]

    def _add_material(self, material):
        material.append_to(Ensurance(self.element).ensure_child('materials'))

    def ensure_material(self, material):
        if self.materials().count(material) == 0:
            self._add_material(material)
        return self

    def git_materials(self):
        return [m for m in self.materials() if m.is_git()]

    def git_material(self):
        gits = self.git_materials()

        if len(gits) == 0:
            raise RuntimeError("pipeline %s has no git" % self)

        if len(gits) > 1:
            raise RuntimeError("pipeline %s has more than one git" % self)

        return gits[0]

    def has_single_git_material(self):
        return len(self.git_materials()) == 1

    def git_url(self):
        return self.git_material().url()

    def git_branch(self):
        return self.git_material().branch()

    def set_git_url(self, git_url):
        return self.set_git_material(GitMaterial(git_url))

    def set_git_material(self, git_material):
        if len(self.git_materials()) > 1:
            raise RuntimeError('Cannot set git url for pipeline that already has multiple git materials. Use "ensure_material(GitMaterial(..." instead')
        PossiblyMissingElement(self.element).possibly_missing_child('materials').remove_all_children('git')
        self._add_material(git_material)
        return self

    def environment_variables(self):
        return ThingWithEnvironmentVariables(self.element).environment_variables()

    def encrypted_environment_variables(self):
        return ThingWithEnvironmentVariables(self.element).encrypted_environment_variables()

    def ensure_environment_variables(self, environment_variables):
        ThingWithEnvironmentVariables(self.element).ensure_environment_variables(environment_variables)
        return self

    def ensure_encrypted_environment_variables(self, environment_variables):
        ThingWithEnvironmentVariables(self.element).ensure_encrypted_environment_variables(environment_variables)
        return self

    def without_any_environment_variables(self):
        ThingWithEnvironmentVariables(self.element).remove_all()
        return self

    def parameters(self):
        param_elements = PossiblyMissingElement(self.element).possibly_missing_child("params").findall("param")
        result = {}
        for param_element in param_elements:
            result[param_element.attrib['name']] = param_element.text
        return result

    def ensure_parameters(self, parameters):
        parameters_ensurance = Ensurance(self.element).ensure_child("params")
        for key, value in parameters.iteritems():
            parameters_ensurance.ensure_child_with_attribute("param", "name", key).set_text(value)
        return self

    def without_any_parameters(self):
        PossiblyMissingElement(self.element).possibly_missing_child("params").remove_all_children()
        return self

    def stages(self):
        return [Stage(stage_element) for stage_element in self.element.findall('stage')]

    def ensure_stage(self, name):
        stage_element = Ensurance(self.element).ensure_child_with_attribute("stage", "name", name)
        return Stage(stage_element._element)

    def ensure_removal_of_stage(self, name):
        matching_stages = [s for s in self.stages() if s.name() == name]
        for matching_stage in matching_stages:
            self.element.remove(matching_stage.element)
        return self

    def ensure_initial_stage(self, name):
        stage = self.ensure_stage(name)
        for stage_element in self.element.findall('stage'):
            if stage_element.attrib['name'] != name:
                self.element.remove(stage_element)
                self.element.append(stage_element)
        return stage

    def reorder_elements_to_please_go(self):
        move_all_to_end(self.element, "params")
        move_all_to_end(self.element, "timer")
        move_all_to_end(self.element, "environmentvariables")
        move_all_to_end(self.element, "materials")
        move_all_to_end(self.element, "stage")

        for stage in self.stages():
            stage.reorder_elements_to_please_go()

    def timer(self):
        if self.has_timer():
            return self.element.find('timer').text
        else:
            raise RuntimeError("%s has no timer" % self)

    def has_timer(self):
        return self.element.find('timer') is not None

    def set_timer(self, timer):
        Ensurance(self.element).ensure_child('timer').set_text(timer)
        return self

    def make_empty(self):
        PossiblyMissingElement(self.element).remove_all_children().remove_attribute('labeltemplate')


DEFAULT_LABEL_TEMPLATE = "0.${COUNT}" # TODO confirm what default really is. I am pretty sure this is mistaken!


class PipelineGroup(CommonEqualityMixin):
    def __init__(self, element):
        self.element = element

    def __repr__(self):
        return 'PipelineGroup("%s")' % self.name()

    def name(self):
        return self.element.attrib['group']

    def pipelines(self):
        return [Pipeline(e, self) for e in self.element.findall('pipeline')]

    def _matching_pipelines(self, name):
        return [p for p in self.pipelines() if p.name() == name]

    def find_pipeline(self, name):
        matching = self._matching_pipelines(name)
        if len(matching) == 0:
            raise RuntimeError('Cannot find pipeline with name "%s" in %s' % (name, self.pipelines()))
        else:
            return matching[0]

    def ensure_pipeline(self, name):
        pipeline_element = Ensurance(self.element).ensure_child_with_attribute('pipeline', 'name', name)._element
        return Pipeline(pipeline_element, self)

    def ensure_removal_of_pipeline(self, name):
        matching_pipelines = self._matching_pipelines(name)
        if len(matching_pipelines) != 0:
            for pipeline in matching_pipelines:
                self.element.remove(pipeline.element)
        return self

    def ensure_replacement_of_pipeline(self, name):
        pipeline = self.ensure_pipeline(name)
        pipeline.make_empty()
        return pipeline


class Agent:
    def __init__(self, element):
        self.thing_with_resources = ThingWithResources(element)

    def resources(self):
        return self.thing_with_resources.resources()

    def ensure_resource(self, resource):
        self.thing_with_resources.ensure_resource(resource)


class HostRestClient:
    def __init__(self, host):
        self._host = host
        self.session_id = None

    def __repr__(self):
        return 'HostRestClient("%s")' % self._host

    def _path(self, path):
        return ('http://%s' % self._host) + path

    def get(self, path):
        r = requests.get(self._path(path))
        self.session_id = r.cookies["JSESSIONID"]
        return r.text

    def post(self, path, data):
        result = requests.post(self._path(path), data, cookies={"JSESSIONID": self.session_id})
        # strangely - you sometimes get a 200 even when there is an error
        if result.status_code != 200 or result.text.count("The following error"):
            open('result.html', 'w').write(result.text)
            webbrowser.open('result.html')
            raise RuntimeError("Could not post config to Go server - see browser to try to work out why")


class GoCdConfigurator:
    def __init__(self, host_rest_client):
        self._host_rest_client = host_rest_client
        self._initial_config = self.current_config()
        self._xml_root = ET.fromstring(self._initial_config)

    def __repr__(self):
        return "GoCdConfigurator(%s)" % self._host_rest_client

    def as_python(self, pipeline, with_save=True):
        result = "#!/usr/bin/env python\nfrom gomatic import *\n\nconfigurator = " + str(self) + "\n"
        result += "pipeline = configurator"
        result += pipeline.as_python_commands_applied_to_server()
        save_part = ""
        if with_save:
            save_part = "\n\nconfigurator.save_updated_config(save_config_locally=True, dry_run=True)"
        return result + save_part

    def current_config(self):
        return self._host_rest_client.get("/go/api/admin/config.xml")

    def reorder_elements_to_please_go(self):
        move_all_to_end(self._xml_root, 'pipelines')
        move_all_to_end(self._xml_root, 'templates')
        move_all_to_end(self._xml_root, 'agents')

        for pipeline in self.pipelines():
            pipeline.reorder_elements_to_please_go()

    def config(self):
        self.reorder_elements_to_please_go()
        return ET.tostring(self._xml_root, 'utf-8')

    def pipeline_groups(self):
        return [PipelineGroup(e) for e in self._xml_root.findall('pipelines')]

    def ensure_pipeline_group(self, group_name):
        pipeline_group_element = Ensurance(self._xml_root).ensure_child_with_attribute("pipelines", "group", group_name)
        return PipelineGroup(pipeline_group_element._element)

    def ensure_removal_of_pipeline_group(self, group_name):
        matching = [g for g in self.pipeline_groups() if g.name() == group_name]
        for group in matching:
            self._xml_root.remove(group.element)
        return self

    def remove_all_pipeline_groups(self):
        for e in self._xml_root.findall('pipelines'):
            self._xml_root.remove(e)
        return self

    def agents(self):
        return [Agent(e) for e in PossiblyMissingElement(self._xml_root).possibly_missing_child('agents').findall('agent')]

    def pipelines(self):
        result = []
        groups = self.pipeline_groups()
        for group in groups:
            result.extend(group.pipelines())
        return result

    def templates(self):
        return [Pipeline(e, 'templates') for e in PossiblyMissingElement(self._xml_root).possibly_missing_child('templates').findall('pipeline')]

    def git_urls(self):
        return [pipeline.git_url() for pipeline in self.pipelines() if pipeline.has_single_git_material()]

    def authenticity_token(self):
        html = self._host_rest_client.get("/go/admin/config_xml/edit")
        line = [l for l in html.split('\n') if l.count('authenticity_token')][0]
        value = [e for e in line.split() if e.count('value')][1]
        return value.split('"')[1]

    def _md5(self, config):
        return hashlib.md5(config).hexdigest()

    def _initial_md5(self):
        return self._md5(self._initial_config)

    def save_updated_config(self, save_config_locally=False, dry_run=False):
        config_before = prettify(self._initial_config)
        config_after = prettify(self.config())
        if save_config_locally:
            open('config-before.xml', 'w').write(config_before)
            open('config-after.xml', 'w').write(config_after)

        data = {
            'go_config[content]': self.config(),
            'commit': 'SAVE',
            '_method': 'put',
            'go_config[md5]': self._initial_md5(),
            'authenticity_token': self.authenticity_token()
        }

        def has_kdiff3():
            try:
                return subprocess.call(["kdiff3", "-version"]) == 0
            except:
                return False

        if save_config_locally and dry_run and config_before != config_after and has_kdiff3():
            subprocess.call(["kdiff3", "config-before.xml", "config-after.xml"])

        if not dry_run and config_before != config_after:
            self._host_rest_client.post('/go/admin/config_xml', data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--server', default='localhost:8153',
                        help='the go server (e.g. "localhost:8153" or "gocd.example.com")')
    parser.add_argument('-d', '--dry-run', action='store_true',
                        help='dry run - do not actually make the changes')
    parser.add_argument('-c', '--do-not-save-config', action='store_true',
                        help='do not save the config locally, before and after making a change (as "config-before.xml" and "config-after.xml")')

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    configurator = GoCdConfigurator(HostRestClient(args.server))

    # do what you want to configurator

    configurator.save_updated_config(save_config_locally=not args.do_not_save_config, dry_run=args.dry_run)
