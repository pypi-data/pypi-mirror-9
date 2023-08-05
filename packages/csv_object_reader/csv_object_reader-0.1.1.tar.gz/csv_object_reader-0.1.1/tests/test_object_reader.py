import unittest
from csv_object_reader import ObjectReader
import tempfile


class EmptyFileTestCase(unittest.TestCase):
    def setUp(self):
        super(EmptyFileTestCase, self).setUp()
        self.raw_file = tempfile.NamedTemporaryFile("a+")
        self.fields = ["color", "weather", "food"]
        self.header = ",".join(self.fields)

    def tearDown(self):
        super(EmptyFileTestCase, self).tearDown()
        self.raw_file.close()

    def write_to_end(self, string):
        self.raw_file.seek(0, 2)
        self.raw_file.write(string)
        self.raw_file.seek(0, 0)


class FileTestCase(EmptyFileTestCase):
    def setUp(self):
        super(FileTestCase, self).setUp()
        self.write_to_end(self.header + "\n")


class ObjectReaderInit(EmptyFileTestCase):
    def setUp(self):
        super(ObjectReaderInit, self).setUp()

    def test_empty_file(self):
        with self.assertRaises(ValueError):
            ObjectReader(self.raw_file)

    def test_empty_header(self):
        self.write_to_end("\n")
        with self.assertRaises(ValueError):
            ObjectReader(self.raw_file)

    def test_malformed_header_field(self):
        self.write_to_end("something bad,test\n")
        with self.assertRaises(ValueError):
            ObjectReader(self.raw_file)

    def test_missing_required_header(self):
        self.write_to_end(self.header + "\n")
        with self.assertRaises(AttributeError):
            ObjectReader(self.raw_file, ["notafield"])

    def test_missing_required_group(self):
        self.write_to_end(self.header + "\n")
        with self.assertRaises(AttributeError):
            ObjectReader(self.raw_file, required_groups=["nota", "notb"])

    def test_good_header(self):
        self.write_to_end(self.header + "\n")
        self.write_to_end("\n")
        ObjectReader(self.raw_file)


class ObjectReaderIter(FileTestCase):
    def setUp(self):
        super(ObjectReaderIter, self).setUp()
        self.entry1 = ["red", "sun", "eggs"]
        self.write_to_end(",".join(self.entry1) + "\n")

    def test_missing_fields(self):
        entry2 = ["red", "", "eggs"]
        self.write_to_end(",".join(entry2) + "\n")
        reader = ObjectReader(self.raw_file)
        expected = [reader.line_type(*self.entry1),
                    reader.line_type(*entry2)]
        result = []
        for line in reader:
            result.append(line)
        self.assertEqual(expected, result)

    def test_good_lines(self):
        reader = ObjectReader(self.raw_file)
        expected = [reader.line_type(*self.entry1)]
        result = []
        for line in reader:
            result.append(line)
        self.assertEqual(expected, result)

    def test_line_not_matching_header(self):
        entry2 = ["red", "eggs"]
        self.write_to_end(",".join(entry2) + "\n")
        reader = ObjectReader(self.raw_file)
        expected = [reader.line_type(*self.entry1)]
        result = []
        for line in reader:
            result.append(line)
        self.assertEqual(expected, result)


class ObjectReaderIterNotEmpty(FileTestCase):
    def setUp(self):
        super(ObjectReaderIterNotEmpty, self).setUp()
        self.entry1 = ["red", "sun", "eggs"]
        self.write_to_end(",".join(self.entry1) + "\n")

    def test_required_field_empty(self):
        entry2 = ["red", "", "eggs"]
        self.write_to_end(",".join(entry2) + "\n")
        reader = ObjectReader(self.raw_file, ["weather"])
        expected = [reader.line_type(*self.entry1)]
        result = []
        for line in reader:
            result.append(line)
        self.assertEqual(expected, result)

    def test_required_group_empty(self):
        entry2 = ["", "", "eggs"]
        self.write_to_end(",".join(entry2) + "\n")
        reader = ObjectReader(self.raw_file,
                              required_groups=[["weather", "color"]])
        expected = [reader.line_type(*self.entry1)]
        result = []
        for line in reader:
            result.append(line)
        self.assertEqual(expected, result)

    def test_good_lines(self):
        entry2 = ["red", "", "eggs"]
        self.write_to_end(",".join(entry2) + "\n")
        reader = ObjectReader(self.raw_file,
                              ["food"],
                              [["color", "weather"]])
        expected = [reader.line_type(*self.entry1),
                    reader.line_type(*entry2)]
        result = []
        for line in reader:
            result.append(line)
        self.assertEqual(expected, result)
