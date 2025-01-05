import yaml

from interaction.agent import Agent

def load_agents_from_yaml(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)

    students = []
    teacher = None
    for obj in data['agents']:
        obj_type = obj['type']
        if obj_type == 'student':
            students.append(Agent(obj['id'], obj['schedule'], obj['style'],
                                  obj['behaviour'], obj['mask'], obj['vaccine']))
        elif obj_type == 'teacher':
            pass
    return students, teacher