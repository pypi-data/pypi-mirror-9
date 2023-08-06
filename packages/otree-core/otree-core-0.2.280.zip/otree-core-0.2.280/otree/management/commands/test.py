
# =============================================================================
# IMPORTS
# =============================================================================

import logging
import sys

from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand

from otree.test import runner, client


# =============================================================================
# CONSTANTS
# =============================================================================

COVERAGE_CONSOLE = "console"
COVERAGE_HTML = "HTML"
COVERAGE_ALL = "all"
COVERAGE_CHOICES = (COVERAGE_ALL, COVERAGE_CONSOLE, COVERAGE_HTML)


# =============================================================================
# LOGGER & Other Conf
# =============================================================================

logger = logging.getLogger(__name__)

settings.SSLIFY_DISABLE = True


# =============================================================================
# COMMAND
# =============================================================================

class Command(BaseCommand):
    help = ('Discover and run experiment tests in the specified '
            'modules or the current directory.')
    option_list = BaseCommand.option_list + (
        make_option(
            '-c', '--coverage', action='store', dest='coverage',
            choices=COVERAGE_CHOICES, help=(
                'Execute code-coverage over the code of '
                'tested experiments [{}]'
            ).format("|".join(COVERAGE_CHOICES))
        ),
        make_option(
            '-t', '--template-vars', action='store_true', dest='tplvars',
            help='Validate the existence of all template vars (Warning)'
        ),
    )
    args = '[experiment_name|experiment_name|experiment_name]...'

    def execute(self, *args, **options):
        if int(options['verbosity']) > 0:
            logger = logging.getLogger('py.warnings')
            handler = logging.StreamHandler()
            logger.addHandler(handler)
        super(Command, self).execute(*args, **options)
        if int(options['verbosity']) > 0:
            logger.removeHandler(handler)

    def handle(self, *test_labels, **options):
        options['verbosity'] = int(options.get('verbosity'))
        if options['verbosity'] < 3:
            logging.basicConfig(level=logging.WARNING)
            logging.getLogger("otree").setLevel(logging.WARNING)
            runner.logger.setLevel(logging.WARNING)
            client.logger.setLevel(logging.WARNING)
        coverage = options["coverage"]

        test_runner = runner.OTreeExperimentTestRunner(**options)

        if options["tplvars"]:
            # this behavior is REAAAALY experimental
            test_runner.patch_validate_missing_template_vars()

        if coverage:
            with runner.covering(test_labels) as coverage_report:
                failures = test_runner.run_tests(test_labels)
        else:
            failures = test_runner.run_tests(test_labels)

        if coverage:
            logger.info("Coverage Report")
            if coverage in [COVERAGE_CONSOLE, COVERAGE_ALL]:
                coverage_report.report()
            if coverage in [COVERAGE_HTML, COVERAGE_ALL]:
                html_coverage_results_dir = '_coverage_results'
                coverage_report.html_report(
                    directory=html_coverage_results_dir
                )
                msg = ("See '{}/index.html' for detailed results.").format(
                    html_coverage_results_dir
                )
                logger.info(msg)

        if failures:
            sys.exit(bool(failures))
