import os
from django.core.management import call_command, CommandError
from django.template import Template
from django.test import TestCase

from otree.checks.templates import get_unreachable_content
from .utils import capture_stdout, dummyapp


class TemplateCheckTest(TestCase):
    def test_non_extending_template(self):
        template = Template('''Stuff in here.''')
        content = get_unreachable_content(template)
        self.assertFalse(content)

        template = Template('''{% block head %}Stuff in here.{% endblock %}''')
        content = get_unreachable_content(template)
        self.assertFalse(content)

        template = Template(
            '''
            Free i am.
            {% block head %}I'm not :({% endblock %}
            ''')
        content = get_unreachable_content(template)
        self.assertEqual(content, [])

    def test_ok_extending_template(self):
        template = Template(
            '''
            {% extends "base.html" %}

            {% block content %}
            Stuff in here.
            {% if 1 %}Un-Conditional{% endif %}
            {% endblock %}
            ''')

        content = get_unreachable_content(template)
        self.assertEqual(content, [])

    def test_extending_template_with_non_wrapped_code(self):
        template = Template(
            '''
            {% extends "base.html" %}

            Free i am.

            {% block content %}Stuff in here.{% endblock %}
            ''')

        content = get_unreachable_content(template)
        self.assertEqual(len(content), 1)
        self.assertTrue('Free i am.' in content[0])
        self.assertTrue('Stuff in here.' not in content[0])

    def test_text_after_block(self):
        template = Template(
            '''
            {% extends "base.html" %}
            {% block content %}Stuff in here.{% endblock %}
            After the block.
            ''')

        content = get_unreachable_content(template)
        self.assertEqual(len(content), 1)
        self.assertTrue('After the block.' in content[0])
        self.assertTrue('Stuff in here.' not in content[0])

    def test_multiple_text_nodes(self):
        template = Template(
            '''
            {% extends "base.html" %}
            First.
            {% block content %}Stuff in here.{% endblock %}
            Second.
            {% load i18n %}
            Third.
            ''')

        content = get_unreachable_content(template)
        self.assertEqual(len(content), 3)
        self.assertTrue('First.' in content[0])
        self.assertTrue('Second.' in content[1])
        self.assertTrue('Third.' in content[2])

    def test_non_block_statements(self):
        # We do not dive into other statements.
        template = Template(
            '''
            {% extends "base.html" %}

            {% if 1 %}
            Free i am.
            {% endif %}
            ''')

        content = get_unreachable_content(template)
        self.assertEqual(len(content), 0)

    def test_ignore_comments(self):
        template = Template(
            '''
            {% extends "base.html" %}
            {# comment #}
            ''')

        content = get_unreachable_content(template)
        self.assertEqual(len(content), 0)

        template = Template(
            '''
            {% extends "base.html" %}
            {% comment %}comment{% endcomment %}
            ''')

        content = get_unreachable_content(template)
        self.assertEqual(len(content), 0)


class TemplateCheckInSystemCheckTest(TestCase):
    def test_check_fails(self):
        with dummyapp('templatecheckapp') as app_path:
            # Runs without issues.
            with capture_stdout():
                call_command('check')

            template_path = os.path.join(
                app_path,
                'templates',
                'templatecheckapp',
                'broken_template.html')
            with open(template_path, 'w') as f:
                f.write(
                    '''
                    {% extends "base.html" %}

                    This file has dead text.
                    ''')

            try:
                with capture_stdout():
                    call_command('check')
            except CommandError as e:
                message = unicode(e)
            else:
                self.fail('Expected check command to fail.')

            # Check for correct app.
            self.assertTrue('templatecheckapp' in message)

            # Check for correct error id.
            self.assertTrue('otree.E005' in message)

            # Check that template name is mentioned.
            path = os.path.join(
                'templatecheckapp',
                'templates',
                'templatecheckapp',
                'broken_template.html')
            self.assertTrue(path in message)

            # Check that dead bits are displayed.
            self.assertTrue('This file has dead text' in message)
