import os
import sys
coverage = None
try:
    from coverage import coverage
except ImportError:
    coverage = None

os.environ['DJANGO_SETTINGS_MODULE'] = 'example_project.settings'
current_dirname = os.path.dirname(__file__)
sys.path.insert(0, current_dirname)
sys.path.insert(0, os.path.join(current_dirname, '..'))


from example_project import settings


def run_tests(settings):
    from django.test.utils import get_runner

    import django
    if hasattr(django, 'setup'):
        django.setup()

    TestRunner = get_runner(settings)
    test_runner = TestRunner(interactive=False)
    failures = test_runner.run_tests(['tests'])
    return failures


def main():
    failures = run_tests(settings)
    sys.exit(failures)


if __name__ == '__main__':
    main()
