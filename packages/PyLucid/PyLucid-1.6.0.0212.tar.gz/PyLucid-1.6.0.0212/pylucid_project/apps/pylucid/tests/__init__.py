#!/usr/bin/env python
# coding: utf-8

import os

if __name__ == "__main__":
    # run all unittest directly
    os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"


from pylucid_project.apps.pylucid.tests.test_Design import *
from pylucid_project.apps.pylucid.tests.test_django_tag_assembler import *
from pylucid_project.apps.pylucid.tests.test_i18n import *
from pylucid_project.apps.pylucid.tests.test_page_permissions import *


if __name__ == "__main__":
    # Run this unittest directly
    from django.core import management
    management.call_command('test', __file__, verbosity=2)

