__author__ = 'alejandrofcarrera'


def get_projects(gl):
    """ Get All Projects
    :param gl: GitLab Object Instance
    :return: Projects List (JSON)
    """
    return gl.git.getprojectsall()


def get_project(gl, project_id):
    """ Get Specific Project
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :return: Project (JSON)
    """
    return gl.git.getproject(project_id)


def get_project_owner(project_id):
    """ Get Specific Project's Owner
    :param project_id: Project Identifier (int)
    :return: Project Owner (JSON)
    """
    return '{"name":"pepe"}'