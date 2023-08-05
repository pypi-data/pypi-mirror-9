#!/usr/bin/env python
import os
import sys

cur_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(cur_dir, '..'))


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.test_settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
    