# Copyright (C) 2011 Diego Pardilla Mata
#
#    This file is part of SpiderBOY.
#
#     SpiderBOY is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from pyPdf import PdfFileReader as Reader

def getPDFContent(path):
    content = ""
    # Load PDF into pyPDF
    pdf = Reader(file(path, "rb"))
    # Iterate pages
    for i in range(0, pdf.getNumPages()):
        # Extract text from page and add to content
        content += pdf.getPage(i).extractText() + "\n"
        # Collapse whitespace

def getPDFlinks (path,proto_filter):
    links = []
    pdf = Reader(file(path, "rb"))
    pages = pdf.getNumPages()
    key = '/Annots'
    uri = '/URI'
    anchor = '/A'
    for page in range(pages):
        pag = pdf.getPage(page)
        obj = pag.getObject()
        if obj.has_key(key):
            list_annots = obj[key]
            #print list_annots
            links = links + [ link.getObject()[anchor][uri] for link in list_annots
                     if (link.getObject().has_key(anchor) and link.getObject()[anchor].has_key(uri) and link.getObject()[anchor][uri].find(proto_filter)==0)]
    return links