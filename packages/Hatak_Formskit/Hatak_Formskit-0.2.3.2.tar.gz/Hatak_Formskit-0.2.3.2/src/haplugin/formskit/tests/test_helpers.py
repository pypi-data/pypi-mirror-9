from mock import MagicMock

from haplugin.toster import TestCase

from ..helpers import FormWidget


class FormWidgetTestCase(TestCase):
    prefix_from = FormWidget

    def setUp(self):
        super().setUp()
        self.form = MagicMock()

        self.widget = FormWidget(self.request, self.form)
        self.add_mock_object(self.widget, 'render_for', autospec=True)

    def assert_render_for(self, result, *args, **kwargs):
        self.assertEqual(
            self.mocks['render_for'].return_value,
            result)
        self.mocks['render_for'].assert_called_once_with(
            *args, **kwargs)

    def test_begin(self):
        """begin should render <form> tag"""
        result = self.widget.begin('fake_id', 'mystyle')

        self.assert_render_for(
            result,
            'begin.jinja2',
            {
                'action': self.form.action,
                'id': 'fake_id',
                'name': self.form.get_name(),
                'style': 'mystyle',
            },)

    def test_end(self):
        """end should render </form> tag"""
        result = self.widget.end()

        self.assert_render_for(
            result,
            'end.jinja2',
            {
            },)

    def test_hidden(self):
        """hidden should render <input type="hidden"> tag"""
        result = self.widget.hidden('myname')
        field = self.form.fields['myname']

        self.assert_render_for(
            result,
            'hidden.jinja2',
            {
                'name': field.get_name(),
                'value': self.form.get_value.return_value,
                'field': field,
            },)

        self.form.get_value.assert_called_once_with('myname', default='')

    def test_submit(self):
        """submit should render <input type="submit"> tag"""
        result = self.widget.submit('mylabel', 'myclass', 'baseclass')

        self.assert_render_for(
            result,
            'submit.jinja2',
            {
                'label': 'mylabel',
                'class': 'myclass',
                'base_class': 'baseclass'
            },)

    def test_error(self):
        """error should render form error html"""
        result = self.widget.error()

        self.assert_render_for(
            result,
            'error.jinja2',
            {
                'error': False,
                'messages': self.form.get_error_messages.return_value,
            },)

    def test_text(self):
        """text should render <input type="text"> tag"""
        self._input_test('text')

    def test_password(self):
        """password should render <input type="password"> tag"""
        self._input_test('password')

    def test_select(self):
        """select should render <input type="select"> tag"""
        self._input_test('select')

    def _input_test(self, name, method_name=None):
        method_name = method_name or name
        input_name = 'myname'

        method = getattr(self.widget, method_name)
        result = method(input_name, True, False)
        field = self.form.fields[name]

        self.assert_render_for(
            result,
            name + '.jinja2',
            {
                'name': field.get_name(),
                'value': self.form.get_value.return_value,
                'field': field,
                'id': '%s_myname' % (self.form.get_name()),
                'label': field.label,
                'error': field.error,
                'messages': (
                    self.form.fields.__getitem__.return_value
                    .get_error_messages.return_value
                ),
                'value_messages': (
                    self.form.fields.__getitem__.return_value
                    .get_value_errors.return_value
                ),
                'disabled': True,
                'autofocus': False,
            },)
