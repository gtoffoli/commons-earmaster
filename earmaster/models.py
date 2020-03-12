from commons.models import Project

def is_earmaster_project(self):
    return self.name.count('Music Education')
Project.is_earmaster = is_earmaster_project