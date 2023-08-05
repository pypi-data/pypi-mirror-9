#!/usr/bin/python
from distutils.core import setup
setup(
  name = 'cs.urlutils',
  description = 'convenience functions for working with URLs',
  author = 'Cameron Simpson',
  author_email = 'cs@zip.com.au',
  version = '20150116',
  url = 'https://bitbucket.org/cameron_simpson/css/commits/all',
  classifiers = ['Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 3', 'Topic :: Software Development :: Libraries :: Python Modules', 'Operating System :: OS Independent', 'Development Status :: 4 - Beta', 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)', 'Intended Audience :: Developers'],
  keywords = ['python2', 'python3'],
  long_description = u'URL facilities.\n===============\n\n* NetrcHTTPPasswordMgr: a subclass of HTTPPasswordMgrWithDefaultRealm that consults the .netrc file if no overriding credentials have been stored.\n\n* URL: factory accepting a URL string returning a str subclass instance with methods and properties to access properties of the URL\n\n-- .NODE: fetch and parse content, return the sole node named "NODE"; example: .TITLE\n\n-- .NODEs: fetch and parse content, return all the nodes named "NODE"; example: .Ps\n\n-- .basename: the basename of the URL path\n\n-- .baseurl: the base URL for this document\n\n-- .content: the content of the document\n\n-- .content_type: the URL Content-Type\n\n-- .dirname: the dirname of the URL path\n\n-- .domain: the hostname part with the first component stripped\n\n-- .feedparsed: a parse of the content via the feedparser module\n\n-- .find_all(): call BeautifulSoup\'s find_all on the parsed content\n\n-- .flush: forget all cached content\n\n-- .fragment: URL fragment as returned by urlparse.urlparse\n\n-- .hostname: the hostname part\n\n-- .hrefs(self, absolute=False): return all URLs cited as href= attributes\n\n-- .netloc: URL netloc as returned by urlparse.urlparse\n\n-- .page_title: the page title, possibly the empty string\n\n-- .params: URL params as returned by urlparse.urlparse\n\n-- .parent: parent URL, the .dirname resolved\n\n-- .parsed: URL content parsed as HTML by BeautifulSoup\n\n-- .parts: URL parsed into parts by urlparse.urlparse\n\n-- .password: URL password as returned by urlparse.urlparse\n\n-- .path: URL path as returned by urlparse.urlparse\n\n-- .path_elements: the non-empty path components\n\n-- .port: URL port as returned by urlparse.urlparse\n\n-- .query: URL query as returned by urlparse.urlparse\n\n-- .scheme: URL scheme as returned by urlparse.urlparse\n\n-- .srcs: return all URLs cited as src= attributes\n\n-- .username: URL username as returned by urlparse.urlparse\n\n-- .xml: content parsed and return as an ElementTree.XML\n\n-- .xml_find_all(self, match): convenience method to call ElementTree.XML\'s .findall() method\n\n',
  package_dir = {'': 'lib/python'},
  py_modules = ['cs.urlutils'],
  requires = ['lxml', 'beautifulsoup4', 'cs.excutils', 'cs.lex', 'cs.logutils', 'cs.threads', 'cs.py3', 'cs.obj'],
)
