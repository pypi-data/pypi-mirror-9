import os

from nose.plugins import Plugin


class DisableDocstring(Plugin):
    """Tells unittest not to use docstrings as test names."""

    name = 'disabledoc'

    def options(self, parser, env=os.environ):
        super(DisableDocstring, self).options(parser, env=env)
        parser.add_option('--disabledoc', action="store_true",
                          help=DisableDocstring.__doc__)

    def configure(self, options, conf):
        super(DisableDocstring, self).configure(options, conf)
        if options.disabledoc:
            self.enabled = True
        if not self.enabled:
            return

    def describeTest(self, test):
        try:
            # First, try and give the TestCase class-based hierarchy
            module_name = test.test.__class__.__module__ + "."
            class_name = test.test.__class__.__name__ + "."
            method_name = test.test._testMethodName
        except:
            # In case something goes wrong, just revert to default behavior
            module_name = ""
            class_name = ""
            method_name = str(test)
        # When nose is wrapping a test function for us, then we don't want
        # class information, just the default behavior
        if module_name in ["nose.case.", "nose.failure."]:
            module_name = ""
            class_name = ""
            method_name = str(test)
        return '%s%s%s' % (module_name, class_name, method_name)
