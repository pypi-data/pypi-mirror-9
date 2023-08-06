# -*- coding: utf-8 -*-
import re
import os
import datetime
try:
    from subprocess import check_output  # noqa
except ImportError:
    def check_output(*args, **kw):
        return None
from mrbob.bobexceptions import ValidationError

def get_git_global(field):
    ret = None
    with open(os.devnull, 'w') as fd:
        ret = check_output(('git config --global %s' % field).split(' '),
                stderr=fd)
    return ret

def _author(configurator, field):
    """Try to get authors info via .mrbob or git"""
    author = None
    try:
        author = configurator.variables[field]
    except:
        pass
    if not author:
        try:
            author = get_git_global(field)
        except:
            pass
    return author

def set_author_question(configurator, question, field):
    author = _author(configurator, field)
    if author:
        question.default = author.strip()

def pre_author(configurator, question):
    """Try to get authors name via user.name or git"""
    set_author_question(configurator, question, 'user.name')

def pre_email(configurator, question):
    """Try to get authors email via user.email or git"""
    set_author_question(configurator, question, 'user.email')

def pre_homepage(configurator, question):
    """Try to get authors homepage via user.homepage or git"""
    set_author_question(configurator, question, 'user.homepage')

valid_pat_r = r'^[A-Za-z][A-Za-z0-9\_]+$'
valid_pat = re.compile(valid_pat_r)

def validate_name(configurator, question, answer):
    """Validate packagename"""
    if not valid_pat.match(answer):
        raise ValidationError('Please use a name that matches %s' %
                valid_pat_r)
    return answer

def _pre_render_copyright(configurator, field, default):
    copyright = _author(configurator, field)
    if not copyright:
        copyright = default
    configurator.variables[field] = copyright

def _pre_render_copyright_name(configurator):
    default_name = configurator.variables.get('python.module.author.name', '')
    _pre_render_copyright(configurator, 'user.copyright_name', default_name)

def _pre_render_copyright_year(configurator):
    default_year = datetime.datetime.now().year
    _pre_render_copyright(configurator, 'user.copyright_year', default_year)

def pre_render(configurator):
    _pre_render_copyright_name(configurator)
    _pre_render_copyright_year(configurator)
