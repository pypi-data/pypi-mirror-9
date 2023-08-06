from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

import unittest

from pydocx.packaging import ZipPackage
from pydocx.util.xml import xml_tag_split
from pydocx.wordml import MainDocumentPart, WordprocessingDocument


class ZipPackageTestCase(unittest.TestCase):
    def setUp(self):
        self.package = ZipPackage(
            path='tests/fixtures/no_break_hyphen.docx',
        )

    def test_relationship_uri(self):
        self.assertEqual(
            self.package.relationship_uri,
            '/_rels/.rels',
        )

    def test_relationship_part_exists(self):
        assert self.package.part_exists(self.package.relationship_uri)

    def test_word_document_part_exists(self):
        assert self.package.part_exists('/word/document.xml')

    def test_package_relationship_part_stream(self):
        part = self.package.get_part('/_rels/.rels')
        data = part.stream.read()
        assert data
        assert data.startswith(b'<?xml version="1.0" encoding="UTF-8"?>')


class WordprocessingDocumentTestCase(unittest.TestCase):
    def setUp(self):
        self.document = WordprocessingDocument(
            path='tests/fixtures/no_break_hyphen.docx',
        )

    def test_document_is_the_open_xml_package(self):
        self.assertEqual(
            self.document,
            self.document.main_document_part.open_xml_package,
        )

    def test_get_parts_of_type_office_document(self):
        self.assertEqual(
            self.document.get_parts_of_type(
                MainDocumentPart.relationship_type,
            )[0],
            self.document.main_document_part,
        )

    def test_main_document_part_uri(self):
        self.assertEqual(
            self.document.main_document_part.uri,
            '/word/document.xml',
        )

    def test_main_document_part_root(self):
        namespace, tag = xml_tag_split(
            self.document.main_document_part.root_element.tag,
        )
        # We're currently ignoring namespaces, so this comes back as none
        self.assertEqual(namespace, None)
        self.assertEqual(tag, 'document')

    def test_main_document_part_relationship_uri(self):
        part = self.document.package.get_part(
            self.document.main_document_part.uri,
        )
        self.assertEqual(
            part.relationship_uri,
            '/word/_rels/document.xml.rels',
        )

    def test_main_document_part_styles_uri(self):
        styles = self.document.main_document_part.style_definitions_part
        self.assertEqual(
            styles.uri,
            '/word/styles.xml',
        )

    def test_main_document_part_font_table_uri(self):
        font_table = self.document.main_document_part.font_table_part
        self.assertEqual(
            font_table.uri,
            '/word/fontTable.xml',
        )

    def test_nonexistent_part(self):
        part = self.document.main_document_part.numbering_definitions_part
        self.assertEqual(part, None)

    def test_image_parts(self):
        image_document = WordprocessingDocument(
            path='tests/fixtures/has_image.docx',
        )
        parts = image_document.main_document_part.image_parts
        self.assertEqual(len(parts), 1)
        self.assertEqual(parts[0].uri, '/word/media/image1.gif')
