#!/usr/bin/python
"""
Handle reading configuration metadata
"""
__author__ = 'dwight'
import configobj


def generate_empty_configuration(filename):
    """
    Generate an empty configuration metadata object
    :param filename:
    :return:
    """
    config = configobj.ConfigObj()
    config.filename = filename

    # Sections
    config['package_info'] = {}
    config['crontab'] = {}
    config['configuration_templates'] = {}
    config['pre_activate_commands'] = {}
    config['post_activate_commands'] = {}
    config['pre_deactivate_commands'] = {}
    config['post_deactivate_commands'] = {}
    config['start_commands'] = {}
    config['stop_commands'] = {}

    config.write()
    return config


def generate_example_configuration(filename):
    """
    Generate an example configuration file
    :param filename:
    """
    config = generate_empty_configuration(filename)
    config['package_info'] = {
        'package_name': 'example',
        'version': '1.0'
    }

    config['crontab']['example'] = '* * * * * example_command'

    config['configuration_templates']['/etc/example.file'] = {
        'template_type': 'jinja',
        'source_file': 'example.jinja'
    }
    config.write()


if __name__ == "__main__":
    generate_example_configuration('/tmp/example.config')