# -*- coding: utf-8 -*-
from tg import url, request
from tg.i18n import ugettext as _
from webhelpers import date, feedgenerator, html, number, misc, text
from tgext.pluggable import app_model, plug_url


def link_buttons(entity, *buttons):
    btns_html = '<div class="turbopress_buttons">'
    for btn in buttons:
        if btn == 'publish' and entity.published:
            continue
        elif btn == 'hide' and not entity.published:
            continue
        elif btn in ('delete', 'rmattachment'):
            btns_html += '''\
    <a href="%(baseurl)s/%(btn)s/%(entity)s" onclick="return confirm('%(confirm_message)s')">
        <img src="/_pluggable/turbopress/buttons/%(btn)s.png"/>
    </a>''' % dict(baseurl=plug_url('turbopress', ''),
                   confirm_message=_('Really delete this?'), btn=btn,
                   entity=entity.uid)
        else:
            btns_html += '''\
    <a href="%(baseurl)s/%(btn)s/%(entity)s">
        <img src="/_pluggable/turbopress/buttons/%(btn)s.png"/>
    </a>''' % dict(baseurl=plug_url('turbopress', ''), btn=btn, entity=entity.uid)
    btns_html += '</div>'

    return html.literal(btns_html)


def comma_separated_tags(entity):
    return ', '.join(entity.tags)


def format_published(entity):
    if entity.published:
        return html.builder.HTML.strong('Published')
    else:
        return 'Draft'


def format_date(entity):
    return entity.publish_date.strftime('%Y-%m-%d %H:%M')


def format_link(url):
    return html.builder.HTML.a(url, href=url, target='_blank')


def attachment_preview(attachment):
    attachment_mime_type = attachment.mimetype
    if attachment_mime_type and attachment_mime_type.startswith('image'):
        preview_url = attachment.url
    else:
        preview_url = "/_pluggable/turbopress/images/unknown.png"
    return html.literal('<img src="%s" class="turbopress_attachment_minipreview"/>' % preview_url)
