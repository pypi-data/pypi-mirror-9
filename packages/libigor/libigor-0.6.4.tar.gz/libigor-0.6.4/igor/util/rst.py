# -*- coding: utf-8 -*-


#----------------------------------------------------------------------------//
def to_html(restText, headerLevel = 1):
    from docutils.core import publish_parts
    overrides = {
        'initial_header_level': headerLevel,
        'doctitle_xform':       False
    }
    parts = publish_parts(source              = restText,
                          writer_name         = 'html',
                          settings_overrides  = overrides)

    # parts['body_pre_docinfo'])
    return parts['html_body']


#----------------------------------------------------------------------------//
def doc2html(restText, headerLevel = 1):
    """ Convert rst document into html extracting the title as well.

    Will only extract the title when it exists. If there is more than one
    root section it won't be treated as the title, Only if its first and one
    of its kind.


    parts contains:
        body        - The html content of the document, without the title.
        title       - The document title.
        html_body   - The document body along with the title.
        html_title  - The document title wrapped in html tags.
    """
    from docutils.core import publish_parts
    overrides = {
        'initial_header_level': headerLevel,
        'doctitle_xform':       True
    }
    parts = publish_parts(source              = restText,
                          writer_name         = 'html',
                          settings_overrides  = overrides)

    return parts['title'], parts['body']


#----------------------------------------------------------------------------//
def get_doctree(rest, headerLevel = 1):
    from docutils.core import publish_doctree
    overrides = {
        'initial_header_level'  : headerLevel,
        'doctitle_xform'        : False
    }
    return publish_doctree(source              = rest,
                           settings_overrides  = overrides)
