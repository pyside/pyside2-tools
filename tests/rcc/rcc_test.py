
import unittest

from PySide.QtCore import QFile

import example_rc

class TestRccSimple(unittest.TestCase):
    def testSimple(self):
        handle = QFile(":words.txt")
        handle.open(QFile.ReadOnly)
        original = open("words.txt", "r")
        self.assertEqual(handle.readLine(), original.readline())

    def testAlias(self):
        handle = QFile(":jack")
        handle.open(QFile.ReadOnly)
        original = open("shining.txt", "r")
        self.assertEqual(handle.readLine(), original.readline())

    def testHuge(self):
        handle = QFile(":manychars.txt")
        handle.open(QFile.ReadOnly)
        original = open("manychars.txt", "r")
        self.assertEqual(handle.readLine(), original.readline())


if __name__ == '__main__':
    unittest.main()
