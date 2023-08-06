# encoding: utf-8
import os
import os.path
from emails.loader.local_store import FileNotFound
from emails.compat import to_unicode
from emails.compat import urlparse
from emails import Message
from emails.utils import fetch_url
from emails.loader import local_store
from emails.loader.helpers import guess_charset


class LoadError(Exception):
    pass


class IndexFileNotFound(LoadError):
    pass


class InvalidHtmlFile(LoadError):
    pass


def from_html(html, source_filename=None, base_url=None, message_params=None, local_loader=None, **kwargs):
    message_params = message_params or {}
    message = Message(html=html, **message_params)
    message.create_transformer(requests_params=kwargs.pop('requests_params', None),
                               base_url=base_url,
                               local_loader=local_loader)
    if message.transformer.tree is None:
        raise InvalidHtmlFile("Error parsing '%s'" % source_filename)
    message.transformer.load_and_transform(**kwargs)
    message.transformer.save()
    return message


from_string = from_html


def from_url(url, requests_params=None, **kwargs):

    def _extract_base_url(url):
        # /a/b.html -> /a
        p = list(urlparse.urlparse(url))[:5]
        p[2] = os.path.split(p[2])[0]
        return urlparse.urlunsplit(p)

    # Load html page
    r = fetch_url(url, requests_args=requests_params)
    html = r.content
    html = to_unicode(html, charset=guess_charset(r.headers, html))
    html = html.replace('\r\n', '\n')  # Remove \r

    return from_html(html,
                     base_url=_extract_base_url(url),
                     source_filename=url,
                     requests_params=requests_params,
                     **kwargs)


load_url = from_url


def _from_filebased_source(store, index_file=None, message_params=None, **kwargs):

    try:
        index_file_name = store.find_index_file(index_file)
    except FileNotFound:
        # reraise another exception
        raise IndexFileNotFound('html file not found')

    dirname, _ = os.path.split(index_file_name)
    if dirname:
        store.base_path = dirname

    return from_html(html=store.content(index_file_name, is_html=True, guess_charset=True),
                     local_loader=store,
                     source_filename=index_file_name,
                     message_params=message_params,
                     **kwargs)


def from_directory(directory, **kwargs):
    return _from_filebased_source(store=local_store.FileSystemLoader(searchpath=directory), **kwargs)


def from_file(filename, **kwargs):
    return from_directory(directory=os.path.dirname(filename), index_file=os.path.basename(filename), **kwargs)


def from_zip(zip_file, **kwargs):
    return _from_filebased_source(store=local_store.ZipLoader(file=zip_file), **kwargs)


def from_rfc822(msg, message_params=None, **kw):

    # Warning: from_rfc822 is for demo purposes only
    # TODO: Implement attachment loading

    store = local_store.MsgLoader(msg=msg)
    text = store['__index.txt']
    html = store['__index.html']

    message_params = message_params or {}
    message = Message(html=html, text=text, **message_params)
    if html:
        message.create_transformer(local_loader=store, **kw)
        message.transformer.load_and_transform()
        message.transformer.save()
    else:
        # TODO: add attachments for text-only message
        pass

    return message