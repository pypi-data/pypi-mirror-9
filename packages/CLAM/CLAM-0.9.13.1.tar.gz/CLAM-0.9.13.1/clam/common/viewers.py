###############################################################
# CLAM: Computational Linguistics Application Mediator
# -- Viewers --
#       by Maarten van Gompel (proycon)
#       http://ilk.uvt.nl/~mvgompel
#       Induction for Linguistic Knowledge Research Group
#       Universiteit van Tilburg
#
#       Licensed under GPLv3
#
###############################################################


try:
    import web
except ImportError:
    pass
import urllib2
from urllib import urlencode
import os.path
from lxml import etree
import csv
from StringIO import StringIO

class AbstractViewer(object):

    id = 'abstractviewer' #you may insert another meaningful ID here, no spaces or special chars!
    name = "Unspecified Viewer"
    mimetype = 'text/html'

    def __init__(self, **kwargs):
        self.embed = False #Embed external sites as opposed to redirecting?
        for key, value in kwargs.items():
            if key == 'embed':
                value = bool(value)
                self.embed = value

    def url(self, file):
        """Returns the URL to view this resource, the link is usually an external service/website. If necessary, the file can be 'pushed' to the service from here. file is a CLAMOutputFile instance"""
        return False

    def view(self, file, **kwargs):
        """Returns the view itself, in xhtml (it's recommended to use web.py's template system!). file is a CLAMOutputFile instance. By default, if not overriden and a remote service is specified, this issues a GET to the remote service."""
        url = self.url(file) + urlencode(kwargs)
        if url: #is the resource external?
            if self.embed:
                #fetch
                req = urllib2.urlopen(url)
                for line in req.readlines():
                    yield line
            else:
                #redirect
                raise web.seeother(url)



class SimpleTableViewer(AbstractViewer):
    id = 'tableviewer'
    name = "Table viewer"

    def __init__(self, **kwargs):
        if 'quotechar' in kwargs:
            self.quotechar = kwargs['quotechar']
            del kwargs['quotechar']
        else:
            self.quotechar = ''

        if 'delimiter' in kwargs:
            self.delimiter = kwargs['delimiter']
            del kwargs['delimiter']
        else:
            self.delimiter = '\t'

        super(SimpleTableViewer,self).__init__(**kwargs)

    def read(self, file):
        #Load all in memory to prevent unicode issues (not ideal)
        data = file.readlines()
        if any( ( isinstance(x, unicode) for x in data ) ):
            data = u"\n".join(data)
            data = data.encode('utf-8')
        else:
            data = "\n".join(data)
        if self.quotechar:
            file = csv.reader(StringIO(data), delimiter=self.delimiter, quotechar=self.quotechar)
        else:
            file = csv.reader(StringIO(data), delimiter=self.delimiter)
        for line in file:
            yield [ unicode(x,'utf-8') for x in line ] #todo, can't really assume utf-8

    def view(self,file,**kwargs):
        render = web.template.render('templates')
        return render.crudetableviewer( file, self)




class FrogViewer(AbstractViewer):
    id = 'frogviewer'
    name = "Frog Viewer"



    def view(self,file,**kwargs):
        render = web.template.render('templates')
        return render.crudetableviewer( file, "\t")

class XSLTViewer(AbstractViewer):
    id = 'xsltviewer'
    name = "XML Viewer"

    def __init__(self, **kwargs):
        if 'file' in kwargs:
            self.xslfile = kwargs['file']
            del kwargs['file']
        else:
            raise Exception("XSLTViewer expect file= parameter with XSL file")

        super(XSLTViewer,self).__init__(**kwargs)

    def view(self, file, **kwargs):
        xslt_doc = etree.parse(self.xslfile)
        transform = etree.XSLT(xslt_doc)

        #f = file.open()
        lines = file.readlines()
        if lines:
            if isinstance(lines[0], unicode):
                xml_doc = etree.parse(StringIO("".join( ( x.encode('utf-8') for x in lines) ) ))
            else:
                xml_doc = etree.parse(StringIO("".join(lines) ))
        else:
            return "(no data)"

        return str(transform(xml_doc))

class FoLiAViewer(AbstractViewer):
    id = 'foliaviewer'
    name = "FoLiA Viewer"

    def view(self, file, **kwargs):
        xslfile = os.path.dirname(__file__) + "/../static/folia.xsl"
        xslt_doc = etree.parse(xslfile)
        transform = etree.XSLT(xslt_doc)

        #f = file.open()

        xml_doc = etree.parse(StringIO("".join(file.readlines()).encode('utf-8')))
        return str(transform(xml_doc))


class SoNaRViewer(AbstractViewer):
    id = 'sonarviewer'
    name = "SoNaR Viewer"

    def view(self, file, **kwargs):
        xslfile = os.path.dirname(__file__) + "/../static/sonar.xsl"
        xslt_doc = etree.parse(xslfile)
        transform = etree.XSLT(xslt_doc)

        #f = file.open()
        xml_doc = etree.parse(StringIO("".join(file.readlines())))

        return str(transform(xml_doc))





