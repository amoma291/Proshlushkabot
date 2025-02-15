import json
import os


def append_to_json(new_data):
    current_data = read_json('questions.json')
    current_data.update(new_data)
    write_json('questions.json', data=current_data)


def join_path(filename):
    file_path = os.path.join(os.path.dirname(__file__), filename)
    return file_path


def read_json(filename):
    file_path = join_path(filename)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def remove_question_from_json(filename, message_id):
    data = read_json(filename)
    if message_id in data:
        del data[message_id]
        write_json(data)


def write_json(filename, data):
    file_path = join_path(filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
