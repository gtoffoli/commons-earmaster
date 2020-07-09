from commons.models import Project

def is_earmaster_project(self):
    project = self
    while project.get_type_name() != 'com':
        # if project.name.count('Music Education'):
        if int(project.id) == 333:
            return True
        project = project.get_parent()
    return False
Project.is_earmaster = is_earmaster_project