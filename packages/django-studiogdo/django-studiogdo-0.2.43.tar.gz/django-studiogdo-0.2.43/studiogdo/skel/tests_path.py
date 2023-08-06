# -*- coding: utf-8 -*-

import json

from django.core.exceptions import SuspiciousOperation
from django.http.response import HttpResponse
from django.test import TestCase
from mock import patch

from path import compose_path
from studiogdo.skel.renderer import HTMLRenderer, PathIterator


class Test(TestCase):
    def test_compose(self):
        path = compose_path('', '')
        self.assertEqual(path, '.')
        path = compose_path('', '.')
        self.assertEqual(path, '.')
        path = compose_path('a', '')
        self.assertEqual(path, 'a')
        path = compose_path('', 'b')
        self.assertEqual(path, 'b')
        path = compose_path('a', 'b')
        self.assertEqual(path, 'a/b')
        path = compose_path('a/b', 'c')
        self.assertEqual(path, 'a/b/c')
        path = compose_path('a', 'b/c')
        self.assertEqual(path, 'a/b/c')
        path = compose_path('a/b', 'c/d')
        self.assertEqual(path, 'a/b/c/d')
        path = compose_path('/', '/', '/')
        self.assertEqual(path, '/')
        path = compose_path('/a', '/b')
        self.assertEqual(path, '/b')
        path = compose_path('/', 'a')
        self.assertEqual(path, '/a')

    def test_compose_with_dot(self):
        path = compose_path('a', '.')
        self.assertEqual(path, 'a')
        path = compose_path('.', 'b')
        self.assertEqual(path, 'b')
        path = compose_path('a/./b', 'c/./d')
        self.assertEqual(path, 'a/b/c/d')
        path = compose_path('/', '.')
        self.assertEqual(path, '/')

    def test_compose_with_parent(self):
        path = compose_path('a/..', 'd/..')
        self.assertEqual(path, '.')
        path = compose_path('a/b/..', 'c/d/..')
        self.assertEqual(path, 'a/c')
        path = compose_path('a/b/..', 'd/..')
        self.assertEqual(path, 'a')
        path = compose_path('a/..', 'd')
        self.assertEqual(path, 'd')
        with self.assertRaises(SuspiciousOperation):
            compose_path('../a')
        with self.assertRaises(SuspiciousOperation):
            compose_path('a', '../..')
        path = compose_path('a/b/c', '../..')
        self.assertEqual(path, 'a')

