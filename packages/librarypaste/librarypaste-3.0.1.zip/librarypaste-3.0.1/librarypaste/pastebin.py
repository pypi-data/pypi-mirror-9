import os
import datetime
import imghdr

import genshi
import cherrypy
import pkg_resources
from pygments.lexers import get_all_lexers, get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments import highlight
from pygments.util import ClassNotFound

from .template import render


BASE = os.path.abspath(os.path.dirname(__file__))

class LexerSorter(object):
    """Takes a list of preferred lexers, and sorts them at the top of the list."""
    def __init__(self, favored_languages):
        self.favored_langs = [x.lower().strip() for x in favored_languages]

    def sort_key_lex(self, l):
        key = l[0].lower()
        for f in self.favored_langs:
            if f in key:
                return 'aaaaaaaaaaaaaaaaaa' + key
        return key


class Server(object):

    def form(self):
        d = {}
        brand_name = cherrypy.request.app.config['branding']['name']
        add_branding(d)
        d['title'] = brand_name + " Paste"

        s = LexerSorter(cherrypy.request.app.config['lexers']['favorites'])
        d['lexers'] = sorted([(l[0], l[1][0]) for l in get_all_lexers()], key=s.sort_key_lex)

        d['pre_nick'] = ('' if not 'paste-nick' in cherrypy.request.cookie
            else cherrypy.request.cookie['paste-nick'].value)
        try:
            d['short'] = bool(int(cherrypy.request.cookie['paste-short'].value))
        except KeyError:
            d['short'] = True
        return render('entry', d)

    @cherrypy.expose
    def index(self, fmt=None, nick='', code=None, file=None, makeshort=None):
        if cherrypy.request.method != 'POST':
            return self.form()
        if code is not None and not isinstance(code, str):
            # workaround for https://bitbucket.org/cherrypy/cherrypy/issue/1352
            code = code.decode('utf-8')
        ds = cherrypy.request.app.config['datastore']['datastore']
        content = dict(
            nick = nick,
            time = datetime.datetime.now(),
            makeshort = bool(makeshort),)
        data = file is not None and file.fullvalue()
        if data:
            filename = file.filename
            mime = str(file.content_type)
            content.update(
                type = 'file',
                mime = mime,
                filename = filename,
                data = data)
            imagetype = imghdr.what(filename, data)
        else:
            content.update(
                type = 'code',
                fmt = fmt,
                code = code,)
        (uid, shortid) = ds.store(**content)

        if nick:
            cherrypy.response.cookie['paste-nick'] = nick
            cherrypy.response.cookie['paste-nick']['expires'] = 60 * 60 * 24 * 30  # store cookies for 30 days

        if makeshort:
            redirid = shortid
            cherrypy.response.cookie['paste-short'] = 1
            cherrypy.response.cookie['paste-short']['expires'] = 60 * 60 * 24 * 30  # store cookies for 30 days
        else:
            redirid = uid
            cherrypy.response.cookie['paste-short'] = 0
            cherrypy.response.cookie['paste-short']['expires'] = 60 * 60 * 24 * 30  # store cookies for 30 days

        if content['type'] == 'file' and not imagetype:
            raise cherrypy.HTTPRedirect(cherrypy.url('file/'+redirid))
        else:
            raise cherrypy.HTTPRedirect(cherrypy.url(redirid))

    @cherrypy.expose
    def default(self, pasteid=None):
        ds = cherrypy.request.app.config['datastore']['datastore']
        d = {}
        add_branding(d)
        try:
            paste_data = ds.retrieve(pasteid)
        except Exception as e:
            print(e)
            raise cherrypy.NotFound("The paste '%s' could not be found." % pasteid)
        if paste_data['type'] == 'file':
            cherrypy.response.headers['Content-Type'] = paste_data['mime']
            cherrypy.response.headers['Content-Disposition'] = 'inline; filename="%s"' % paste_data['filename']
            cherrypy.response.headers['filename'] = paste_data['filename']
            return paste_data['data']

        total_lines = paste_data['code'].count('\n') + 1
        line_nums = map(str, range(1, total_lines + 1))
        d['linenums'] = '\n'.join(line_nums)
        if paste_data['fmt'] == '_':
            lexer = get_lexer_by_name('text')
        else:
            try:
                lexer = get_lexer_by_name(paste_data['fmt'])
            except ClassNotFound:
                lexer = get_lexer_by_name('text')
        htmlformatter = HtmlFormatter(linenos='table')
        code = highlight(paste_data['code'], lexer, htmlformatter)
        d['code'] = genshi.Markup(code)
        d['pasteid'] = pasteid
        d['plainurl'] = cherrypy.url('plain/' + pasteid)
        d['homeurl'] = cherrypy.url('')
        d['title'] = 'Paste %s%s%s%s on %s' % (
            '%s aka ' % paste_data['shortid'] if 'shortid' in paste_data else '',
            paste_data['uid'] if 'uid' in paste_data else pasteid,
            ' (%s)' % paste_data['fmt'] if paste_data['fmt'] != '_' else '',
            ' by %s' % paste_data['nick'] if 'nick' in paste_data else '',
            paste_data['time'].strftime('%b %d, %H:%M'))
        return render('view', d)

    @cherrypy.expose
    def last(self, nick=''):
        ds = cherrypy.request.app.config['datastore']['datastore']
        last = ds.lookup(nick)
        if not last:
            raise cherrypy.NotFound(nick)
        raise cherrypy.HTTPRedirect(cherrypy.url('/'+last))

    @cherrypy.expose
    def plain(self, pasteid=None):
        ds = cherrypy.request.app.config['datastore']['datastore']
        paste_data = ds.retrieve(pasteid)
        cherrypy.response.headers['Content-Type'] = 'text/plain'
        return paste_data['code']

    @cherrypy.expose
    def file(self, pasteid=''):
        d = {}
        add_branding(d)
        d['title'] = "File link for %s" % pasteid
        d['link'] = cherrypy.url('/' + pasteid)
        return render('file', d)

    @cherrypy.expose
    def about(self):
        d = {}
        add_branding(d)
        info = pkg_resources.require('librarypaste')[0]
        d['title'] = 'About Library Paste'
        d['version'] = info.version
        return render('about', d)

def add_branding(context):
    context.update(
        brand_name = cherrypy.request.app.config['branding']['name'],
        logo_src = cherrypy.request.app.config['branding']['logo source'],
    )
