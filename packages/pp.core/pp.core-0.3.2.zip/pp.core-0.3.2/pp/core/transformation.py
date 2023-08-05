################################################################
# pp.core - Produce & Publish
# (C) 2013, ZOPYX Limited, www.zopyx.com
################################################################

import inspect
import time
import lxml.etree
import lxml.html

from pp.core.logger import LOG

TRANSFORMATIONS = dict()

def registerTransformation(method):
    """ Decorator to register a method as a transformation"""
    name = method.__name__
    if name in TRANSFORMATIONS:
        raise ValueError('Transformation "{}" already registered'.format(name))
    TRANSFORMATIONS[name] = method


def availableTransformations():
    return TRANSFORMATIONS.keys()


def hasTransformations(transformations):
    available_transformations = availableTransformations()
    for t in transformations:
        if not t in available_transformations:
            return False
    return True


class Transformer(object):

    def __init__(self, transformation_names, context=None, destdir=None, **params):
        self.transformation_names = transformation_names
        self.context = context
        self.destdir = destdir
        self.params = params

    def __call__(self, html, input_encoding=None, output_encoding=unicode, return_body=False):

        if not isinstance(html, unicode):
            if not input_encoding:
                raise TypeError('Input data must be unicode')
            html = unicode(html, input_encoding)

        html = html.strip()
        if not html:
            return u''

        root = lxml.html.fromstring(html)
        errors = list()

        for name in self.transformation_names:
            method = TRANSFORMATIONS.get(name)
            params = dict(context=self.context,
                          request=getattr(self.context, 'REQUEST', None),
                          destdir=self.destdir,
                          )
            params.update(self.params)
            if method is None:
                raise ValueError('No transformation "%s" registered' % name)

            ts = time.time()
            argspec = inspect.getargspec(method)
            
            kw = {}
            if 'params' in (argspec.keywords or ()):
                kw.update(params)
            if 'errors' in (argspec.keywords or ()):
                kw['errors'] = errors

            method(root, **kw)
            LOG.info('Transformation %-30s: %3.6f seconds' % (name, time.time()-ts))

        if errors:
            LOG.error('SOME ERRORS OCCURED')
        for error in errors:
            LOG.error(error)

        if return_body:
            nodes = root.xpath('//body')
            if nodes:
                body = nodes[0]
            elif not nodes:
                nodes = root.xpath('//article')
                if nodes:
                    body = nodes[0]
                elif not nodes:
                    raise RuntimeError('Neither <body> nor <article> tags found')
            html_new = (body.text or '') + u''.join([lxml.html.tostring(b, encoding=output_encoding, pretty_print=True) for b in body])

        else:
            html_new = lxml.html.tostring(root, encoding=output_encoding, pretty_print=True)
            if html_new.startswith('<div>') and html_new.endswith('</div>'):
                html_new = html_new[5:-6].strip()

        return html_new.strip()


class TransformerXML(Transformer):

    def __call__(self, xml, input_encoding='utf-8', output_encoding=unicode): 
        """ UTF8 in, UTF8 out """

        if not isinstance(xml, unicode):
            if not input_encoding:
                raise TypeError('Input data must be unicode')
            xml = unicode(xml, input_encoding)

        xml = xml.strip()
        if not xml:
            return ''

        root = lxml.html.fromstring(xml)
        errors = list()

        for name in self.transformation_names:
            method = TRANSFORMATIONS.get(name)
            params = dict(context=self.context,
                          request=getattr(self.context, 'REQUEST', None),
                          destdir=self.destdir,
                          )
            params.update(self.params)
            if method is None:
                raise ValueError('No transformation "%s" registered' % name)

            ts = time.time()
            argspec = inspect.getargspec(method)

            kw = {}
            if 'params' in argspec.keywords:
                kw.update(params)
            if 'errors' in argspec.keywords:
                kw['errors'] = errors

            method(root, **kw)
            LOG.info('Transformation %-30s: %3.6f seconds' % (name, time.time()-ts))

        if errors:
            LOG.error('SOME ERRORS OCCURED')
        for error in errors:
            LOG.error(error)

        if output_encoding == unicode:
            return lxml.etree.tostring(
                    root, 
                    encoding=unicode, 
                    pretty_print=True)
        else:
            return lxml.etree.tostring(
                    root.getroottree(), 
                    encoding=output_encoding,
                    xml_declaration=True,
                    pretty_print=True)



def xpath_query(node_names):
    if not isinstance(node_names, (list, tuple)):
        raise TypeError('"node_names" must be a list or tuple (not %s)' % type(node_names))
    return './/*[%s]' % ' or '.join(['name()="%s"' % name for name in node_names])

