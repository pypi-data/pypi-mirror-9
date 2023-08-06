# everythin now lives in logilab.packaging

from logilab.common.deprecation import class_moved, moved
from logilab.devtools.lib import deprecation_msg
from logilab.packaging.lib.pkginfo import PackageInfo

PackageInfo = class_moved(PackageInfo, message=deprecation_msg)

for fname in ('check_info_module',
              'check_url',
              'get_default_arch_dep',
              'get_default_catalog',
              'get_default_depends',
              'get_default_documentation',
              'get_default_dtd_files',
              'get_default_elisp_files',
              'get_default_elisp_startup',
              'get_default_examples_dir',
              'get_default_handler',
              'get_default_html_documentation',
              'get_default_license_text',
              'get_default_man_files',
              'get_default_recommends',
              'get_default_scripts',
              'get_default_suggests',
              'get_default_test_dir',
              'get_default_xslt_files',
              'get_known_licenses',
              'get_license_text',
              'pkginfo_save',
              'sequence_equal',
              'spell_check'
              ):
    globals()[fname] = moved('logilab.packaging.lib.pkginfo', fname)

