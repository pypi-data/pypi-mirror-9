"""
The functionality itself for each task.

Each task is specified with the ``a_task`` decorator and indicates whether it's
necessary to provide the task with the object containing all the stacks and/or
one specific stack object.
"""

from bespin.amazon.ec2 import display_instances
from bespin.actions.builder import Builder
import itertools
import logging

log = logging.getLogger("bespin.tasks")

available_tasks = {}
class a_task(object):
    """Records a task in the ``available_tasks`` dictionary"""
    def __init__(self, needs_artifact=False, needs_stack=False, needs_stacks=False, needs_credentials=False):
        self.needs_artifact = needs_artifact
        self.needs_stack = needs_stack
        self.needs_stacks = needs_stack or needs_stacks
        self.needs_credentials = needs_credentials

    def __call__(self, func):
        available_tasks[func.__name__] = func
        func.needs_artifact = self.needs_artifact
        func.needs_stack = self.needs_stack
        func.needs_stacks = self.needs_stacks
        func.needs_credentials = self.needs_credentials
        return func

@a_task()
def list_tasks(overview, configuration, **kwargs):
    """List the available_tasks"""
    print("Available tasks to choose from are:")
    print("Use the --task option to choose one")
    print("")
    keygetter = lambda item: item[1].label
    tasks = sorted(overview.find_tasks().items(), key=keygetter)
    for label, items in itertools.groupby(tasks, keygetter):
        print("--- {0}".format(label))
        print("----{0}".format("-" * len(label)))
        sorted_tasks = sorted(list(items), key=lambda item: len(item[0]))
        max_length = max(len(name) for name, _ in sorted_tasks)
        for key, task in sorted_tasks:
            print("\t{0}{1} :-: {2}".format(" " * (max_length-len(key)), key, task.description or ""))
        print("")

@a_task(needs_stacks=True)
def show(overview, configuration, stacks, **kwargs):
    """Show what stacks we have"""
    flat = configuration.get("bespin.flat", False)
    only_pushable = configuration.get("bespin.only_pushable", False)

    for index, layer in enumerate(Builder().layered(stacks, only_pushable=only_pushable)):
        if flat:
            for _, stack in layer:
                print(stack.stack_name)
        else:
            print("Layer {0}".format(index))
            for _, stack in layer:
                print("    {0}".format(stack.display_line()))
            print("")

@a_task(needs_stack=True, needs_credentials=True)
def deploy(overview, configuration, stacks, stack, credentials, artifact, **kwargs):
    """Deploy a particular stack"""
    Builder().deploy_stack(stack, stacks, credentials)

@a_task(needs_stack=True, needs_credentials=True)
def publish_artifacts(overview, configuration, stacks, stack, credentials, artifact, **kwargs):
    """Build and publish an artifact"""
    Builder().publish_artifacts(stack, credentials)

@a_task(needs_stack=True, needs_credentials=True)
def clean_old_artifacts(overview, configuration, stacks, stack, credentials, artifact, **kwargs):
    """Cleanup old artifacts"""
    Builder().clean_old_artifacts(stack, credentials)

@a_task(needs_stack=True, needs_credentials=True)
def confirm_deployment(overview, configuration, stacks, stack, credentials, artifact, **kwargs):
    """Confirm deployment via SNS notification for each instance"""
    Builder().confirm_deployment(stack, credentials)

@a_task(needs_stack=True, needs_artifact=True)
def print_artifact_location(overview, configuration, stacks, stack, credentials, artifact, **kwargs):
    """Shows where the artifact will be for this environment"""
    Builder().print_artifact_location(stack, artifact)

@a_task(needs_stack=True, needs_credentials=True)
def suspend_cloudformation_actions(overview, configuration, stacks, stack, credentials, artifact, **kwargs):
    """Suspends all schedule actions on a cloudformation stack"""
    Builder().suspend_cloudformation_actions(stack, credentials)

@a_task(needs_stack=True, needs_credentials=True)
def resume_cloudformation_actions(overview, configuration, stacks, stack, credentials, artifact, **kwargs):
    """Resumes all schedule actions on a cloudformation stack"""
    Builder().resume_cloudformation_actions(stack, credentials)

@a_task(needs_stack=True)
def sanity_check(overview, configuration, stacks, stack, artifact, **kwargs):
    """Sanity check a stack and it's dependencies"""
    Builder().sanity_check(stack, stacks)
    log.info("All the stacks are sane!")

@a_task(needs_stack=True, needs_credentials=True)
def instances(overview, configuration, stacks, stack, artifact, **kwargs):
    """Find and ssh into instances"""
    if artifact is None:
        asg_physical_id = stack.cloudformation.map_logical_to_physical_resource_id(stack.ssh.autoscaling_group_name)
        display_instances(stack.bespin.credentials, asg_physical_id)
    else:
        stack.ssh.ssh_into(artifact, configuration["$@"])

@a_task(needs_stack=True)
def bastion(overview, configuration, stacks, stack, **kwargs):
    """SSH into the bastion"""
    stack.ssh.ssh_into_bastion(configuration["$@"])

