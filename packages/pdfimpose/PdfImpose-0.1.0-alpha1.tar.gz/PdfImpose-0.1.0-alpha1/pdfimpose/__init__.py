#!/usr/bin/env python3

# Copyright Louis Paternault 2011-2014
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>. 1

"""Perform imposition of a PDF file.

TODO explain example

.. code-block:: python

    from pdfimpose import impose, VERTICAL, HORIZONTAL

    impose(
        inname="foo.pdf",
        outname="foo-impose.pdf",
        fold=[VERTICAL, HORIZONTAL],
        bind="left",
        last=0,
        )

High level manipulation
-----------------------

TODO

.. autofunction:: impose

Direction
^^^^^^^^^

TODO

.. autodata:: VERTICAL
.. autodata:: HORIZONTAL
.. autoclass:: Direction


Low level manipulation
----------------------

These objects will usually not be manipulated directly by user. They are used
internally may be manipulated if finer processing is performed.

Orientation
^^^^^^^^^^^

TODO

.. autoclass:: Orientation

.. autodata:: NORTH
.. autodata:: SOUTH

Imposition objects
^^^^^^^^^^^^^^^^^^

TODO

.. autoclass:: Coordinates

.. autoclass:: ImpositionPage

.. autoclass:: ImpositionMatrix

Performing imposition
^^^^^^^^^^^^^^^^^^^^^

TODO

.. autofunction:: imposition_matrix

.. autofunction:: pypdf_impose

"""

from PyPDF2.generic import NameObject, createStringObject
from enum import Enum
import PyPDF2
import logging
import math

VERSION = "0.1.0-alpha1"
__AUTHOR__ = "Louis Paternault (spalax@gresille.org)"
__COPYRIGHT__ = "(C) 2014 Louis Paternault. GNU GPL 3 or later."

LOGGER = logging.getLogger(__name__)

class Direction(Enum):
    """Direction (horizontal or vertical)"""
    # pylint: disable=too-few-public-methods

    vertical = False
    horizontal = True

    def __str__(self):
        return self.name[0].upper()

    @classmethod
    def from_char(cls, char):
        """Return :class:`Direction` object corresponding to `char`.

        Character can be one of `h` or `v`, ignoring case.
        """
        if char.lower() == 'h':
            return cls.horizontal
        elif char.lower() == 'v':
            return cls.vertical
        else:
            raise ValueError(
                "{}: Argument '{}' is not recognised as a direction.".format(
                    cls.__name__,
                    char
                    )
                )

VERTICAL = Direction.vertical
HORIZONTAL = Direction.horizontal

class Orientation(Enum):
    """Two dimensions orientation"""
    # pylint: disable=too-few-public-methods

    north = 90
    south = 270

    def __str__(self):
        return self.name[0].upper()

    def fold(self, rotate):
        """Return the symmetrical orientation.

        :param bool rotate: Should page be rotated?
        """
        if rotate:
            return Orientation((-self.value) % 360)
        else:
            return Orientation((180 - self.value) % 360)

NORTH = Orientation.north
SOUTH = Orientation.south
_ORIENTATION_MATRIX = {
    NORTH.value: [1, 0, 0, 1],
    SOUTH.value: [-1, 0, 0, -1],
    }

class Coordinates:
    """Two-dimensions coordinates."""
    # pylint: disable=too-few-public-methods

    x = 0
    y = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Coordinates(
            self.x + other.x,
            self.y + other.y,
            )

    def __sub__(self, other):
        return Coordinates(
            self.x - other.x,
            self.y - other.y,
            )

    def __str__(self):
        return "({}, {})".format(self.x, self.y)

    def __repr__(self):
        return "{}({}, {})".format(
            self.__class__.__name__,
            self.x,
            self.y,
            )

class ImpositionPage:
    """Page, on an imposition matrix: a page number, and an orientation."""
    # pylint: disable=too-few-public-methods

    def __init__(self, number, orientation):
        self.orientation = orientation
        self.number = number

    def __str__(self):
        return "{: 3}{}".format(
            self.number,
            self.orientation,
            )

    def fold(self, page_max, rotate):
        """Return the symmetrical page to `self`.

        :arg bool orientation: Fold orientation.
        :arg int page_max: Maximum page number.
        """
        return ImpositionPage(
            page_max - self.number,
            self.orientation.fold(rotate),
            )

class ImpositionMatrix:
    """Matrix of an imposition: array of numbered, oriented pages."""
    folds = []

    def __init__(self, size, bind):
        self.matrix = [
            [
                None
                for y
                in range(size.y)
                ]
            for x
            in range(2*size.x)
            ]
        self.bind = bind
        if bind in ["top", "right"]:
            self.matrix[0][0] = ImpositionPage(0, NORTH)
        else: # bind in ["bottom", "left"]:
            self.matrix[-1][-1] = ImpositionPage(0, NORTH)
        self.fold(HORIZONTAL, rotate=(bind in ["top", "bottom"]))

    @property
    def vfolds(self):
        """Return the number of vertical folds"""
        return self.folds.count(VERTICAL)

    @property
    def hfolds(self):
        """Return the number of horizontal folds"""
        return self.folds.count(HORIZONTAL)

    @property
    def size(self):
        """Return the size of the matrix, as a :class:`Coordinates`."""
        return Coordinates(
            len(self.matrix),
            len(self.matrix[0]),
            )

    def fold(self, orientation, rotate=None):
        """Perform a fold according to `orientation`."""
        if rotate is None:
            if orientation == HORIZONTAL:
                rotate = (self.bind in ["top", "bottom"])
            else:
                rotate = (self.bind in ["left", "right"])
        metapage_size = Coordinates(
            self.size.x//2**self.hfolds,
            self.size.y//2**self.vfolds,
            )
        for x in range(0, self.size.x, metapage_size.x):
            for y in range(0, self.size.y, metapage_size.y):
                self._metapage_fold(
                    Coordinates(x, y),
                    metapage_size,
                    orientation,
                    rotate,
                    )
        self.folds.append(orientation)

    def __getitem__(self, *item):
        if len(item) == 1:
            item = item[0]
            if isinstance(item, Coordinates):
                return self.matrix[item.x][item.y] # pylint: disable=no-member
        elif len(item) == 2:
            if isinstance(item[0], int) and isinstance(item[1], int):
                return self.matrix[item[0]][item[1]]
        raise TypeError()

    def __setitem__(self, item, value):
        if len(item) == 1:
            item = item[0]
            if isinstance(item, Coordinates):
                self.matrix[item.x][item.y] = value
                return
        elif len(item) == 2:
            if isinstance(item[0], int) and isinstance(item[1], int):
                self.matrix[item[0]][item[1]] = value
                return
        raise TypeError()

    def _metapage_find_page(self, corner, size):
        """Find the actual page on a metapage.

        A metapage should contain only one actual page. Return the coorditanes
        of this page (relative to the matrix).

        :arg Coordinates corner: Coordinates of the low left corner of the
            metapage.
        :arg Coordinates size: Size of the metapage.
        """
        for coordinates in [
                corner,
                corner + Coordinates(size.x-1, 0),
                corner + Coordinates(0, size.y-1),
                corner + size - Coordinates(1, 1),
            ]:
            if self[coordinates] is not None:
                return coordinates

    def _metapage_fold(self, corner, size, orientation, rotate):
        """Fold a metapage

        :arg Coordinates corner: Low left corner of the metapage.
        :arg Coordinates size: Size of the metapage.
        :arg bool orientation: Fold orientation.
        :arg bool rotate: Should pages be rotated?
        """
        page = self._metapage_find_page(corner, size)
        if orientation == HORIZONTAL:
            self[
                2 * corner.x + size.x - page.x - 1, # Vertical symmetrical
                page.y,
                ] = self[page].fold(2**(len(self.folds)+1)-1, rotate)
        else:
            self[
                page.x,
                2 * corner.y + size.y - page.y - 1, # Horizontal symmetrical
                ] = self[page].fold(2**(len(self.folds)+1)-1, rotate)

    def __str__(self):
        return "\n".join([
            " ".join([
                str(page)
                for page
                in row
                ])
            for row
            in reversed(list(zip(*self.matrix))) # pylint: disable=star-args
            ])

    @property
    def recto(self):
        """Return the recto of matrix."""
        return self.matrix[len(self.matrix)//2:]

    @property
    def verso(self):
        """Return the verso of matrix."""
        return self.matrix[:len(self.matrix)//2]

def imposition_matrix(folds, bind):
    """Return the imposition matrix.

    :param list folds: Sorted list of folds, as a list of :class:`Direction`
        instances.
    :param str bind: One of ``top``, ``bottom``, ``left``, ``right``: edge on
        which the final book is to be folded.
    """
    matrix = ImpositionMatrix(
        Coordinates(
            2**folds.count(HORIZONTAL),
            2**folds.count(VERTICAL),
            ),
        bind,
        )
    for i in folds:
        matrix.fold(i)
    return matrix

def _get_input_pages(pdfsize, sectionsize, section_number, last):
    """Return the input pages, with `None` added to fit `sectionsize`."""
    return (
        [i for i in range(pdfsize - last)] +
        [None for i in range(pdfsize, section_number * sectionsize)] +
        [i for i in range(pdfsize - last, pdfsize)]
        )

def _get_pdf_size(page):
    """Return the size (width x height) of page."""
    return (
        page.mediaBox.lowerRight[0] - page.mediaBox.lowerLeft[0],
        page.mediaBox.upperRight[1] - page.mediaBox.lowerRight[1],
        )

def _set_metadata(inpdf, outpdf):
    """Copy and set metadata from inpdf to outpdf.
    """
    #Source:
    #    http://two.pairlist.net/pipermail/reportlab-users/2009-November/009033.html
    try:
        # pylint: disable=protected-access
        # Since we are accessing to a protected membre, which can no longer exist
        # in a future version of PyPDF2, we prevent errors.
        infodict = outpdf._info.getObject()
        infodict.update(inpdf.getDocumentInfo())
        infodict.update({
            NameObject('/Creator'): createStringObject(
                'PdfImpose, using the PyPDF2 library — http://TODO'
                )
        })
    except AttributeError:
        LOGGER.warning("Could not copy metadata from source document.")

def pypdf_impose(matrix, pdf, last, callback=None):
    """Return the pdf object corresponding to imposition of ``pdf``.

    TODO param
    """
    # pylint: disable=too-many-locals

    if callback is None:
        callback = lambda x, y: None
    width, height = _get_pdf_size(pdf.getPage(0))
    output = PyPDF2.PdfFileWriter()

    sectionsize = matrix.size.x * matrix.size.y
    section_number = math.ceil(pdf.numPages / sectionsize)
    inputpages = _get_input_pages(pdf.numPages, sectionsize, section_number, last)
    rectoverso = [matrix.verso, matrix.recto]
    pagecount = 0
    for outpagenumber in range(2 * section_number):
        currentoutputpage = output.addBlankPage(
            matrix.size.x * width // 2,
            matrix.size.y * height,
            )
        for x in range(len(rectoverso[outpagenumber%2])):
            for y in range(len(rectoverso[outpagenumber%2][x])):
                pagenumber = (
                    (outpagenumber//2)*sectionsize
                    + rectoverso[outpagenumber%2][x][y].number
                    )
                if inputpages[pagenumber] is not None:
                    if rectoverso[outpagenumber%2][x][y].orientation == NORTH:
                        currentoutputpage.mergeTransformedPage(
                            pdf.getPage(inputpages[pagenumber]),
                            _ORIENTATION_MATRIX[NORTH.value] + [x*width, y*height],
                            )
                    else:
                        currentoutputpage.mergeTransformedPage(
                            pdf.getPage(inputpages[pagenumber]),
                            _ORIENTATION_MATRIX[SOUTH.value] + [(x+1)*width, (y+1)*height],
                            )
                    pagecount += 1
                    callback(pagecount, pdf.numPages)

    _set_metadata(pdf, output)
    return output

def impose(inname, outname, fold, bind, last, callback=None):
    """TODO"""
    # pylint: disable=too-many-arguments
    pypdf_impose(
        matrix=imposition_matrix(fold, bind),
        pdf=PyPDF2.PdfFileReader(inname),
        last=last,
        callback=callback,
        ).write(outname)

