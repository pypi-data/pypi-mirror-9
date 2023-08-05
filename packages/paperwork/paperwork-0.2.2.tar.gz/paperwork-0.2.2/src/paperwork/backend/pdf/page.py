#    Paperwork - Using OCR to grep dead trees the easy way
#    Copyright (C) 2012-2014  Jerome Flesch
#
#    Paperwork is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Paperwork is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Paperwork.  If not, see <http://www.gnu.org/licenses/>.

import cairo
import codecs
import os
import logging
import pyocr
import pyocr.builders

from paperwork.backend.common.page import BasicPage
from paperwork.backend.util import split_words
from paperwork.backend.util import surface2image


# By default, PDF are too small for a good image rendering
# so we increase their size
PDF_RENDER_FACTOR = 2
logger = logging.getLogger(__name__)


class PdfWordBox(object):
    def __init__(self, content, rectangle, pdf_size):
        self.content = content
        # XXX(Jflesch): Coordinates seem to come from the bottom left of the
        # page instead of the top left !?
        self.position = ((int(rectangle.x1 * PDF_RENDER_FACTOR),
                          int((pdf_size[1] - rectangle.y2)
                              * PDF_RENDER_FACTOR)),
                         (int(rectangle.x2 * PDF_RENDER_FACTOR),
                          int((pdf_size[1] - rectangle.y1)
                              * PDF_RENDER_FACTOR)))


class PdfLineBox(object):
    def __init__(self, word_boxes, rectangle, pdf_size):
        self.word_boxes = word_boxes
        # XXX(Jflesch): Coordinates seem to come from the bottom left of the
        # page instead of the top left !?
        self.position = ((int(rectangle.x1 * PDF_RENDER_FACTOR),
                          int((pdf_size[1] - rectangle.y2)
                              * PDF_RENDER_FACTOR)),
                         (int(rectangle.x2 * PDF_RENDER_FACTOR),
                          int((pdf_size[1] - rectangle.y1)
                              * PDF_RENDER_FACTOR)))


class PdfPage(BasicPage):
    EXT_TXT = "txt"
    EXT_BOX = "words"

    def __init__(self, doc, page_nb):
        BasicPage.__init__(self, doc, page_nb)
        self.pdf_page = doc.pdf.get_page(page_nb)
        assert(self.pdf_page is not None)
        size = self.pdf_page.get_size()
        self._size = (int(size[0]), int(size[1]))
        self.__boxes = None
        self.__img_cache = {}
        doc = doc

    def get_doc_file_path(self):
        """
        Returns the file path of the image corresponding to this page
        """
        return self.doc.get_pdf_file_path()

    def __get_txt_path(self):
        return self._get_filepath(self.EXT_TXT)

    def __get_box_path(self):
        return self._get_filepath(self.EXT_BOX)

    def __get_last_mod(self):
        try:
            return os.stat(self.__get_box_path()).st_mtime
        except OSError:
            return 0.0

    last_mod = property(__get_last_mod)

    def _get_text(self):
        txtfile = self.__get_txt_path()

        try:
            os.stat(txtfile)

            txt = []
            try:
                with codecs.open(txtfile, 'r', encoding='utf-8') as file_desc:
                    for line in file_desc.readlines():
                        line = line.strip()
                        txt.append(line)
            except IOError, exc:
                logger.error("Unable to read [%s]: %s" % (txtfile, str(exc)))
            return txt

        except OSError, exc:  # os.stat() failed
            pass

        boxfile = self.__get_box_path()
        try:
            os.stat(boxfile)

            # reassemble text based on boxes
            boxes = self.boxes
            txt = []
            for line in boxes:
                txt_line = u""
                for box in line.word_boxes:
                    txt_line += u" " + box.content
                txt.append(txt_line)
            return txt
        except OSError, exc:
            txt = self.pdf_page.get_text()
            txt = unicode(txt, encoding='utf-8')
            return txt.split(u"\n")

    def __get_boxes(self):
        """
        Get all the word boxes of this page.
        """
        if self.__boxes is not None:
            return self.__boxes

        # Check first if there is an OCR file available
        boxfile = self.__get_box_path()
        try:
            os.stat(boxfile)

            box_builder = pyocr.builders.LineBoxBuilder()

            try:
                with codecs.open(boxfile, 'r', encoding='utf-8') as file_desc:
                    self.__boxes = box_builder.read_file(file_desc)
                return self.__boxes
            except IOError, exc:
                logger.error("Unable to get boxes for '%s': %s"
                             % (self.doc.docid, exc))
                # will fall back on pdf boxes
        except OSError, exc:  # os.stat() failed
            pass

        # fall back on what libpoppler tells us

        # TODO: Line support !

        txt = self.pdf_page.get_text()
        pdf_size = self.pdf_page.get_size()
        words = set()
        self.__boxes = []
        for line in txt.split("\n"):
            for word in split_words(unicode(line, encoding='utf-8')):
                words.add(word)
        for word in words:
            for rect in self.pdf_page.find_text(word):
                word_box = PdfWordBox(word, rect, pdf_size)
                line_box = PdfLineBox([word_box], rect, pdf_size)
                self.__boxes.append(line_box)
        return self.__boxes

    def __set_boxes(self, boxes):
        boxfile = self.__get_box_path()
        with codecs.open(boxfile, 'w', encoding='utf-8') as file_desc:
            pyocr.builders.LineBoxBuilder().write_file(file_desc, boxes)
        self.drop_cache()
        self.doc.drop_cache()

    boxes = property(__get_boxes, __set_boxes)

    def __render_img(self, factor):
        # TODO(Jflesch): In a perfect world, we shouldn't use ImageSurface.
        # we should draw directly on the GtkImage.window.cairo_create()
        # context. It would be much more efficient.

        if factor not in self.__img_cache:
            logger.debug('Building img from pdf with factor: %s'
                         % factor)
            width = int(factor * self._size[0])
            height = int(factor * self._size[1])

            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
            ctx = cairo.Context(surface)
            ctx.scale(factor, factor)
            self.pdf_page.render(ctx)
            self.__img_cache[factor] = surface2image(surface)
        return self.__img_cache[factor]

    def __get_img(self):
        return self.__render_img(PDF_RENDER_FACTOR)

    img = property(__get_img)

    def __get_size(self):
        return (self._size[0] * PDF_RENDER_FACTOR,
                self._size[1] * PDF_RENDER_FACTOR)

    size = property(__get_size)

    def print_page_cb(self, print_op, print_context, keep_refs={}):
        ctx = print_context.get_cairo_context()

        logger.debug("Context: %d x %d" % (print_context.get_width(),
                                           print_context.get_height()))
        logger.debug("Size: %d x %d" % (self._size[0], self._size[1]))

        factor_x = float(print_context.get_width()) / float(self._size[0])
        factor_y = float(print_context.get_height()) / float(self._size[1])
        factor = min(factor_x, factor_y)

        logger.debug("Scale: %f x %f --> %f" % (factor_x, factor_y, factor))

        ctx.scale(factor, factor)

        self.pdf_page.render_for_printing(ctx)
        return None
