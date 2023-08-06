#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from tests.hacking import checks
from tests.unit import test


class HackingTestCase(test.TestCase):

    def test__parse_assert_mock_str(self):
        pos, method, obj = checks._parse_assert_mock_str(
            "mock_clients.fake().quotas.delete.assert_called_once()")
        self.assertEqual("assert_called_once", method)
        self.assertEqual("mock_clients.fake().quotas.delete", obj)

    def test__parse_assert_mock_str_no_assert(self):
        pos, method, obj = checks._parse_assert_mock_str(
            "mock_clients.fake().quotas.delete.")
        self.assertIsNone(pos)
        self.assertIsNone(method)
        self.assertIsNone(obj)

    def test_correct_usage_of_assert_from_mock(self):
        correct_method_names = ["assert_any_call", "assert_called_once_with",
                                "assert_called_with", "assert_has_calls"]
        for name in correct_method_names:
            self.assertEqual(0, len(
                list(checks.check_assert_methods_from_mock(
                    "some_mock.%s(asd)" % name, "./tests/fake/test"))))

    def test_wrong_usage_of_broad_assert_from_mock(self):
        fake_method = "rtfm.assert_something()"

        actual_number, actual_msg = next(checks.check_assert_methods_from_mock(
            fake_method, "./tests/fake/test"))
        self.assertEqual(4, actual_number)
        self.assertTrue(actual_msg.startswith("N301"))

    def test_wrong_usage_of_assert_called_from_mock(self):
        fake_method = "rtfm.assert_called()"

        actual_number, actual_msg = next(checks.check_assert_methods_from_mock(
            fake_method, "./tests/fake/test"))
        self.assertEqual(4, actual_number)
        self.assertTrue(actual_msg.startswith("N302"))

    def test_wrong_usage_of_assert_called_once_from_mock(self):
        fake_method = "rtfm.assert_called_once()"

        actual_number, actual_msg = next(checks.check_assert_methods_from_mock(
            fake_method, "./tests/fake/test"))
        self.assertEqual(4, actual_number)
        self.assertTrue(actual_msg.startswith("N303"))

    def test_check_wrong_logging_import(self):
        bad_imports = ["from oslo_log import log",
                       "import oslo_log",
                       "import logging"]
        good_imports = ["from rally.common import log",
                        "from rally.common.log",
                        "import rally.common.log"]

        for bad_import in bad_imports:
            checkres = checks.check_import_of_logging(bad_import, "fakefile")
            self.assertIsNotNone(next(checkres))

        for bad_import in bad_imports:
            checkres = checks.check_import_of_logging(bad_import,
                                                      "./rally/common/log.py")
            self.assertEqual([], list(checkres))

        for good_import in good_imports:
            checkres = checks.check_import_of_logging(good_import,
                                                      "fakefile")
            self.assertEqual([], list(checkres))

    def test_no_translate_debug_logs(self):
        self.assertEqual(len(list(checks.no_translate_debug_logs(
            "LOG.debug(_('foo'))"))), 1)

        self.assertEqual(len(list(checks.no_translate_debug_logs(
            "LOG.debug('foo')"))), 0)

        self.assertEqual(len(list(checks.no_translate_debug_logs(
            "LOG.info(_('foo'))"))), 0)

    def test_no_use_conf_debug_check(self):
        self.assertEqual(len(list(checks.no_use_conf_debug_check(
            "if CONF.debug:", "fakefile"))), 1)

        self.assertEqual(len(list(checks.no_use_conf_debug_check(
            "if cfg.CONF.debug", "fakefile"))), 1)

        self.assertEqual(len(list(checks.no_use_conf_debug_check(
            "if logging.is_debug()", "fakefile"))), 0)

    def test_assert_true_instance(self):
        self.assertEqual(len(list(checks.assert_true_instance(
            "self.assertTrue(isinstance(e, "
            "exception.BuildAbortException))"))), 1)

        self.assertEqual(
            len(list(checks.assert_true_instance("self.assertTrue()"))), 0)

    def test_assert_equal_type(self):
        self.assertEqual(len(list(checks.assert_equal_type(
            "self.assertEqual(type(als['QuicAssist']), list)"))), 1)

        self.assertEqual(
            len(list(checks.assert_equal_type("self.assertTrue()"))), 0)

    def test_check_iteritems_method(self):
        self.assertEqual(len(list(checks.check_iteritems_method(
            "dict.iteritems()"))), 1)

        self.assertEqual(len(list(checks.check_iteritems_method(
            "iteritems(dict)"))), 0)

        self.assertEqual(len(list(checks.check_iteritems_method(
            "dict.items()"))), 0)

    def test_check_concatenate_dict_with_plus_operand(self):
        self.assertEqual(len(list(
            checks.check_concatenate_dict_with_plus_operand(
                "dict1.items() + dict2.items()"))), 1)

        self.assertEqual(len(list(
            checks.check_concatenate_dict_with_plus_operand(
                "dict(self.endpoint.to_dict().items() + "
                "endpoint.items())"))), 1)

        self.assertEqual(len(list(
            checks.check_concatenate_dict_with_plus_operand(
                "dict(self.endpoint.to_dict().items() + "
                "endpoint.items() + something.items())"))), 1)

        self.assertEqual(len(list(
            checks.check_concatenate_dict_with_plus_operand(
                "dict1.item() + dict2.item()"))), 0)

        self.assertEqual(len(list(
            checks.check_concatenate_dict_with_plus_operand(
                "obj.getitems() + obj.getitems()"))), 0)

        self.assertEqual(len(list(
            checks.check_concatenate_dict_with_plus_operand(
                "obj.getitems() + dict2.items()"))), 0)

    def test_check_basestring_method(self):
        self.assertEqual(len(list(checks.check_basestring_method(
            "basestring"))), 1)

        self.assertEqual(len(list(checks.check_basestring_method(
            "six.string_types"))), 0)

    def test_check_StringIO_method(self):
        self.assertEqual(len(list(checks.check_StringIO_method(
            "StringIO.StringIO()"))), 1)

        self.assertEqual(len(list(checks.check_StringIO_method(
            "six.moves.StringIO()"))), 0)

    def test_check_urlparse_method(self):
        self.assertEqual(len(list(checks.check_urlparse_method(
            "urlparse.urlparse(url)"))), 1)

        self.assertEqual(len(list(checks.check_urlparse_method(
            "six.moves.urllib.parse.urlparse(url)"))), 0)

    def test_check_itertools_imap_method(self):
        self.assertEqual(len(list(checks.check_itertools_imap_method(
            "itertools.imap()"))), 1)

        self.assertEqual(len(list(checks.check_itertools_imap_method(
            "six.moves.map()"))), 0)

    def test_check_xrange_imap_method(self):
        self.assertEqual(len(list(checks.check_xrange_method(
            "xrange()"))), 1)

        self.assertEqual(len(list(checks.check_xrange_method(
            "six.moves.range()"))), 0)

    def test_check_string_lower_upper_case_method(self):
        self.assertEqual(len(list(checks.check_string_lower_upper_case_method(
            "string.lowercase[:16]"))), 1)

        self.assertEqual(len(list(checks.check_string_lower_upper_case_method(
            "string.uppercase[:16]"))), 1)

        self.assertEqual(len(list(checks.check_string_lower_upper_case_method(
            "string.ascii_lowercase[:16]"))), 0)

        self.assertEqual(len(list(checks.check_string_lower_upper_case_method(
            "string.ascii_uppercase[:16]"))), 0)

    def test_check_next_on_iterator_method(self):
        self.assertEqual(len(list(checks.check_next_on_iterator_method(
            "iterator.next()"))), 1)

        self.assertEqual(len(list(checks.check_next_on_iterator_method(
            "next(iterator)"))), 0)

    def test_assert_equal_none(self):
        self.assertEqual(len(list(checks.assert_equal_none(
            "self.assertEqual(A, None)"))), 1)

        self.assertEqual(len(list(checks.assert_equal_none(
            "self.assertEqual(None, A)"))), 1)

        self.assertEqual(
            len(list(checks.assert_equal_none("self.assertIsNone()"))), 0)

    def test_assert_true_or_false_with_in_or_not_in(self):
        self.assertEqual(len(list(checks.assert_true_or_false_with_in(
            "self.assertTrue(A in B)"))), 1)

        self.assertEqual(len(list(checks.assert_true_or_false_with_in(
            "self.assertFalse(A in B)"))), 1)

        self.assertEqual(len(list(checks.assert_true_or_false_with_in(
            "self.assertTrue(A not in B)"))), 1)

        self.assertEqual(len(list(checks.assert_true_or_false_with_in(
            "self.assertFalse(A not in B)"))), 1)

        self.assertEqual(len(list(checks.assert_true_or_false_with_in(
            "self.assertTrue(A in B, 'some message')"))), 1)

        self.assertEqual(len(list(checks.assert_true_or_false_with_in(
            "self.assertFalse(A in B, 'some message')"))), 1)

        self.assertEqual(len(list(checks.assert_true_or_false_with_in(
            "self.assertTrue(A not in B, 'some message')"))), 1)

        self.assertEqual(len(list(checks.assert_true_or_false_with_in(
            "self.assertFalse(A not in B, 'some message')"))), 1)

        self.assertEqual(len(list(checks.assert_true_or_false_with_in(
            "self.assertTrue(A in 'some string with spaces')"))), 1)

        self.assertEqual(len(list(checks.assert_true_or_false_with_in(
            "self.assertTrue(A in 'some string with spaces')"))), 1)

        self.assertEqual(len(list(checks.assert_true_or_false_with_in(
            "self.assertTrue(A in ['1', '2', '3'])"))), 1)

        self.assertEqual(len(list(checks.assert_true_or_false_with_in(
            "self.assertTrue(A in [1, 2, 3])"))), 1)

        self.assertEqual(len(list(checks.assert_true_or_false_with_in(
            "self.assertTrue(any(A > 5 for A in B))"))), 0)

        self.assertEqual(len(list(checks.assert_true_or_false_with_in(
            "self.assertTrue(any(A > 5 for A in B), 'some message')"))), 0)

        self.assertEqual(len(list(checks.assert_true_or_false_with_in(
            "self.assertFalse(some in list1 and some2 in list2)"))), 0)

    def test_assert_equal_in(self):
        self.assertEqual(len(list(checks.assert_equal_in(
            "self.assertEqual(a in b, True)"))), 1)

        self.assertEqual(len(list(checks.assert_equal_in(
            "self.assertEqual(a not in b, True)"))), 1)

        self.assertEqual(len(list(checks.assert_equal_in(
            "self.assertEqual('str' in 'string', True)"))), 1)

        self.assertEqual(len(list(checks.assert_equal_in(
            "self.assertEqual('str' not in 'string', True)"))), 1)

        self.assertEqual(len(list(checks.assert_equal_in(
            "self.assertEqual(any(a==1 for a in b), True)"))), 0)

        self.assertEqual(len(list(checks.assert_equal_in(
            "self.assertEqual(True, a in b)"))), 1)

        self.assertEqual(len(list(checks.assert_equal_in(
            "self.assertEqual(True, a not in b)"))), 1)

        self.assertEqual(len(list(checks.assert_equal_in(
            "self.assertEqual(True, 'str' in 'string')"))), 1)

        self.assertEqual(len(list(checks.assert_equal_in(
            "self.assertEqual(True, 'str' not in 'string')"))), 1)

        self.assertEqual(len(list(checks.assert_equal_in(
            "self.assertEqual(True, any(a==1 for a in b))"))), 0)

        self.assertEqual(len(list(checks.assert_equal_in(
            "self.assertEqual(a in b, False)"))), 1)

        self.assertEqual(len(list(checks.assert_equal_in(
            "self.assertEqual(a not in b, False)"))), 1)

        self.assertEqual(len(list(checks.assert_equal_in(
            "self.assertEqual('str' in 'string', False)"))), 1)

        self.assertEqual(len(list(checks.assert_equal_in(
            "self.assertEqual('str' not in 'string', False)"))), 1)

        self.assertEqual(len(list(checks.assert_equal_in(
            "self.assertEqual(any(a==1 for a in b), False)"))), 0)

        self.assertEqual(len(list(checks.assert_equal_in(
            "self.assertEqual(False, a in b)"))), 1)

        self.assertEqual(len(list(checks.assert_equal_in(
            "self.assertEqual(False, a not in b)"))), 1)

        self.assertEqual(len(list(checks.assert_equal_in(
            "self.assertEqual(False, 'str' in 'string')"))), 1)

        self.assertEqual(len(list(checks.assert_equal_in(
            "self.assertEqual(False, 'str' not in 'string')"))), 1)

        self.assertEqual(len(list(checks.assert_equal_in(
            "self.assertEqual(False, any(a==1 for a in b))"))), 0)

    def test_check_no_direct_rally_objects_import(self):

        bad_imports = ["from rally.objects import task",
                       "import rally.objects.task"]

        good_import = "from rally import objects"

        for bad_import in bad_imports:
            checkres = checks.check_no_direct_rally_objects_import(bad_import,
                                                                   "fakefile")
            self.assertIsNotNone(next(checkres))

        for bad_import in bad_imports:
            checkres = checks.check_no_direct_rally_objects_import(
                bad_import, "./rally/objects/__init__.py")
            self.assertEqual([], list(checkres))

        checkres = checks.check_no_direct_rally_objects_import(good_import,
                                                               "fakefile")
        self.assertEqual([], list(checkres))

    def test_check_no_oslo_deprecated_import(self):

        bad_imports = ["from oslo.config",
                       "import oslo.config,"
                       "from oslo.db",
                       "import oslo.db,"
                       "from oslo.i18n",
                       "import oslo.i18n,"
                       "from oslo.serialization",
                       "import oslo.serialization,"
                       "from oslo.utils",
                       "import oslo.utils,"]

        for bad_import in bad_imports:
            checkres = checks.check_no_oslo_deprecated_import(bad_import,
                                                              "fakefile")
            self.assertIsNotNone(next(checkres))
