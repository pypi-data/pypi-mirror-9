import tg
from tg.i18n import lazy_ugettext as l_
from tgext.ajaxforms import ajaxloaded
from tgext.pluggable import plug_url
from turbopress.lib.validators import NaiveDateTimeValidator
from tw2.core import CSSLink, Required
from tw2.forms import DataGrid
from tw2.forms import ListForm, TextField, TextArea, HiddenField, FileField, SubmitButton
from formencode.validators import UnicodeString, FieldStorageUploadConverter


class SpinnerIcon(object):
    @property
    def link(self):
        return tg.url('/_pluggable/turbopress/images/spinner.gif')


def inject_datagrid_resources(dg):
    resources = [r.req() for r in dg.resources]
    for r in resources:
        r.prepare()


class ArticleForm(ListForm):
    uid = HiddenField()
    title = TextField(label='Title',
                      container_attrs={'class': 'form-group'}, css_class='form-control',
                      validator=UnicodeString(not_empty=True, outputEncoding=None))
    description = TextField(label='Description',
                            container_attrs={'class': 'form-group'}, css_class='form-control',
                            validator=UnicodeString(outputEncoding=None),
                            placeholder=l_('If empty will be extracted from the content'))
    tags = TextField(label='Tags',
                     container_attrs={'class': 'form-group'}, css_class='form-control',
                     validator=UnicodeString(outputEncoding=None),
                     placeholder=l_('tags, comma separated'))
    content = TextArea(label=None, key='content', name='content', id="article_content",
                       container_attrs={'class': 'form-group'}, css_class='form-control',
                       validator=UnicodeString(not_empty=True, outputEncoding=None))
    publish_date = TextField(label='Publish Date', type='datetime-local',
                             container_attrs={'class': 'form-group'}, css_class='form-control',
                             validator=NaiveDateTimeValidator(not_empty=True))

    submit = SubmitButton(value=l_('Save'), css_class="btn btn-primary")

@ajaxloaded
class UploadForm(ListForm):
    css_class = "form-inline"

    article = HiddenField()
    name = TextField(label=None, placeholder=l_('Name'),
                     container_attrs={'class': 'form-group'}, css_class='form-control',
                     validator=UnicodeString(not_empty=True, outputEncoding=None))
    file = FileField(label=None,
                     container_attrs={'class': 'form-group'}, css_class='form-control',
                     validator=FieldStorageUploadConverter(not_empty=True))

    action = plug_url('turbopress', '/attach', lazy=True)
    ajaxurl = plug_url('turbopress', '/upload_form_show', lazy=True)

    submit = SubmitButton(value='Attach', label=None, css_class="btn btn-info")


class SearchForm(ListForm):
    css_class = "form-inline"

    blog = HiddenField()
    text = TextField(label=None, validator=UnicodeString(not_empty=True, outputEncoding=None),
                     container_attrs={'class': 'form-group'}, css_class='form-control',
                     placeholder=l_('Search...'))
    submit_btn = SubmitButton(value='Search', container_attrs={'class': 'form-group'},
                              css_class="form-control btn btn-default")
    submit = None


def get_article_form():
    config = tg.config['_turbopress']

    article_form = config.get('form_instance')
    if not article_form:
        form_path = config.get('form', 'turbopress.lib.forms.ArticleForm')
        module, form_name = form_path.rsplit('.', 1)
        module = __import__(module, fromlist=form_name)
        form_class = getattr(module, form_name)
        article_form = config['form_instance'] = form_class()

    return article_form
