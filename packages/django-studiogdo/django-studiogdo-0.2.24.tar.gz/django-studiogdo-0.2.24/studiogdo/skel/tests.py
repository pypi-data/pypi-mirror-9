# -*- coding: utf-8 -*-

import json

from django.core.exceptions import SuspiciousOperation
from django.http.response import HttpResponse
from django.test import TestCase
from mock import patch

from path import compose_path
from studiogdo.skel.renderer import HTMLRenderer, PathIterator


class TestPath(TestCase):
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


class TestExtractPathes(TestCase):
    @patch('studiogdo.api.StudiogdoApi')
    def test_simple(self, mock_studiogdo):
        renderer = HTMLRenderer(mock_studiogdo, debug=True)

        skel = '<div debug="pass">test</div>'
        pathes = renderer.extract_pathes(skel)
        self.assertEqual(pathes, set([]))

        skel = '<div data-cond="condition">test</div>'
        pathes = renderer.extract_pathes(skel)
        self.assertEqual(pathes, {"condition"})

        skel = '<div data-cond="!condition">test</div>'
        pathes = renderer.extract_pathes(skel)
        self.assertEqual(pathes, {"condition"})

        skel = '<div data-cond=".">test</div>'
        pathes = renderer.extract_pathes(skel)
        self.assertEqual(pathes, {"."})

        skel = '<div data-cond="!">test</div>'
        pathes = renderer.extract_pathes(skel)
        self.assertEqual(pathes, {"."})

        skel = '<div data-value="prop">test</div>'
        pathes = renderer.extract_pathes(skel)
        self.assertEqual(pathes, {"prop"})

        skel = """
        <div data-path='path' data-value='prop'>
            <span data-value='prop'></span>
        </div>
        """
        pathes = renderer.extract_pathes(skel)
        self.assertEqual(pathes, {"path", "prop", "path/prop"})

        skel = """
        <div data-path='path' data-value='prop'>
            <span data-path='comp' data-value='prop'></span>
        </div>
        """
        pathes = renderer.extract_pathes(skel)
        self.assertEqual(pathes, {"path", "prop", "path/prop", "path/comp"})

        skel = """
        <div data-path='path' data-value='prop'>
            <span data-value='comp/prop'></span>
        </div>
        """
        pathes = renderer.extract_pathes(skel)
        self.assertEqual(pathes, {"path", "prop", "path/comp/prop"})

        skel = """
        <div data-path='path' data-value='prop'>
            <span data-value='prop1'></span>
            <span data-value='prop2'></span>
        </div>
        """
        pathes = renderer.extract_pathes(skel)
        self.assertEqual(pathes, {"path", "prop", "path/prop1", "path/prop2"})

        skel = """
        <select data-label='Nom'>
            <option data-path='Fixation' data-value='Id' data-label='Nom' />
        </select>
        """
        pathes = renderer.extract_pathes(skel)
        self.assertEqual(pathes, {"Nom", PathIterator("Fixation", {"Id", "Nom"})})

        skel = """
        <select data-path="path" data-label='Nom'>
            <option data-path='Fixation' data-value='Id' data-label='Nom' />
        </select>
        """
        pathes = renderer.extract_pathes(skel)
        self.assertEqual(pathes, {"path", "Nom", PathIterator("path/Fixation", {"Id", "Nom"})})

        skel = """
        <select data-cond="!path" data-label='Nom'>
            <option data-path='Fixation' data-value='Id' data-label='Nom' />
        </select>
        """
        pathes = renderer.extract_pathes(skel)
        self.assertEqual(pathes, {"path", "Nom", PathIterator("Fixation", {"Id", "Nom"})})

        skel = """
        <table>
            <thead><tr data-path='Fixation'>
                <th data-value='Id' />
                <th data-value='Nom' />
            </tr></thead>
        </table>
        """
        pathes = renderer.extract_pathes(skel)
        self.assertEqual(pathes, {PathIterator("Fixation", {"Id", "Nom"})})

        skel = """
        <table data-path='.'>
            <thead><tr data-path='Fixation'>
                <th data-value='Id' />
                <th data-value='Nom' />
            </tr></thead>
        </table>
        """
        pathes = renderer.extract_pathes(skel)
        self.assertEqual(pathes, {".", PathIterator("Fixation", {"Id", "Nom"})})

        skel = """
        <table data-path='Support'>
            <thead><tr data-path='Fixation'>
                <th data-value='Id' />
                <th data-value='Nom' />
            </tr></thead>
        </table>
        """
        pathes = renderer.extract_pathes(skel)
        self.assertEqual(pathes, {"Support", PathIterator("Support/Fixation", {"Id", "Nom"})})

        with open('studiogdo/skel/examples/ex1.skel', 'r') as content_file:
            skel = content_file.read()
        pathes = renderer.extract_pathes(skel)
        inp = {".", "Adresse", "Adresse/Adresse1", "Adresse/Adresse2", "Adresse/CodePostal", "Adresse/Ville", "Adresse/Pays"}
        self.assertEqual(pathes, inp)

        with open('studiogdo/skel/examples/ex2.skel', 'r') as content_file:
            skel = content_file.read()
        pathes = renderer.extract_pathes(skel)
        ths = {"DateCommande", "SocieteFact", "NomFact", "DateLivraison"}
        tds = {"Id", "Transporteur", "prixFactTotalTTCAffiche", "SuiviTransport"}
        self.assertEqual(pathes, {".", PathIterator("CommandeValide", ths.union(tds))})

        for i in range(0, 0):
            with open('studiogdo/skel/examples/ex3.skel', 'r') as content_file:
                skel = content_file.read()
            pathes = renderer.extract_pathes(skel)
            ths = {"DateLivraison", "SocieteFact", "PrixFactHT", "prixFactTotalHT", "prixFactTotalTTCAffiche"}
            tds = {".^", "Id", "ReferenceClient", "DateCommande", "Status", "Delai", "NomFact", "PrenomFact", "ModePaiement", "TimePaiement"}
            self.assertEqual(pathes, {PathIterator(".", ths.union(tds))})


class TestRenderer(TestCase):
    @patch('studiogdo.api.StudiogdoApi')
    def test_renderer_cond(self, mock_studiogdo):
        renderer = HTMLRenderer(mock_studiogdo, debug=True)

        skel = '<div debug="pass">test</div>'
        res = renderer.render('/', skel)
        self.assertRegexpMatches(res, 'debug="pass">test</div>')
        self.assertFalse(mock_studiogdo.called)

        values = [{"data-path": "/", "Id": 0}]
        js = json.dumps({"data-path": "/", "data-value": values})
        mock_studiogdo.get_list.return_value.content = js
        skel = '<div data-cond="condition">test</div>'
        res = renderer.render('/', skel)
        self.assertEqual(res.strip(), "")
        self.assertTrue(mock_studiogdo.get_list.called)

        values = [{"data-path": "/", "condition": "test", "Id": 0}]
        js = json.dumps({"data-path": "/", "data-value": values})
        mock_studiogdo.get_list.return_value.content = js
        skel = '<div data-cond="!condition">test</div>'
        res = renderer.render('/', skel)
        self.assertEqual(res.strip(), "")
        self.assertTrue(mock_studiogdo.get_list.called)

        values = [{"data-path": "/", "condition": "test", "Id": 0}]
        js = json.dumps({"data-path": "/", "data-value": values})
        mock_studiogdo.get_list.return_value.content = js
        skel = '<div data-cond="condition">test</div>'
        res = renderer.render('/', skel)
        self.assertRegexpMatches(res, 'debug="pass">test</div>')
        self.assertTrue(mock_studiogdo.get_list.called)

    @patch('studiogdo.api.StudiogdoApi')
    def test_renderer_container(self, mock_studiogdo):
        renderer = HTMLRenderer(mock_studiogdo, debug=True)

        values = [{"data-path": "/", ".": "/", "prop": "test", "Id": 0}]
        js = json.dumps({"data-path": "/", "data-value": values})
        mock_studiogdo.get_list.return_value.content = js
        skel = "<span data-value='prop'></span>"
        res = renderer.render('/', skel)
        self.assertRegexpMatches(res, 'test')

        skel = "<span data-path='.'>test</span>"
        res = renderer.render('/', skel)
        self.assertRegexpMatches(res, 'test')

        skel = "<span data-path='!'>test</span>"
        res = renderer.render('/', skel)
        self.assertEquals(res, '')

    @patch('studiogdo.api.StudiogdoApi')
    def test_renderer_container_and_child(self, mock_studiogdo):
        renderer = HTMLRenderer(mock_studiogdo, debug=True)

        values = [{"data-path": "/", "path": "test1", "prop": "test3", "path/prop": "test2", "Id": 0}]
        js = json.dumps({"data-path": "/", "data-value": values})
        mock_studiogdo.get_list.return_value.content = js
        skel = """<div data-path='path' data-value='prop'>
            <span data-value='prop'></span>
        </div>"""
        res = renderer.render('/', skel, mode="text")
        self.assertEqual(res.strip(), "test3test3")

        values = [{"data-path": "/", "path": "test1", "prop": "test3", "path/prop": "test2", "Id": 0}]
        js = json.dumps({"data-path": "/", "data-value": values})
        mock_studiogdo.get_list.return_value.content = js
        skel = """<div data-path='path' data-value='prop'>
            <span data-value='path/prop'></span>
        </div>"""
        res = renderer.render('/', skel, mode="text")
        self.assertEqual(res.strip(), "test2test3")
        self.assertTrue(mock_studiogdo.get_list.called)

    @patch('studiogdo.api.StudiogdoApi')
    def test_renderer_container_not(self, mock_studiogdo):
        renderer = HTMLRenderer(mock_studiogdo, debug=True)

        values = [{"data-path": "/", "path": "test1", "prop": "test3", "path/prop": "test2", "Id": 0}]
        js = json.dumps({"data-path": "/", "data-value": values})
        mock_studiogdo.get_list.return_value.content = js
        skel = """<div data-cond='!path'>
            test
        </div>"""
        res = renderer.render('/', skel)
        self.assertTrue(mock_studiogdo.get_list.called)
        self.assertRegexpMatches(res, '')

        values = [{"data-path": "/", "Id": 0}]
        js = json.dumps({"data-path": "/", "data-value": values})
        mock_studiogdo.get_list.return_value.content = js
        mock_studiogdo.post_facet.return_value.content = ""
        skel = """<div data-cond='!path'>
            test
        </div>"""
        res = renderer.render('/', skel)
        self.assertTrue(mock_studiogdo.get_list.called)
        self.assertRegexpMatches(res.strip(), 'test')

    @patch('studiogdo.api.StudiogdoApi')
    def test_renderer_final(self, mock_studiogdo):
        renderer = HTMLRenderer(mock_studiogdo, debug=True)

        values = [{"data-path": "/", "prop": "aBc", "/prop": "aBc", "Id": 0}]
        js = json.dumps({"data-path": "/", "data-value": values})
        mock_studiogdo.get_list.return_value.content = js

        skel = "<progress data-value='prop'></progress>"
        res = renderer.render('/', skel, mode="text")
        self.assertEqual(res, 'aBc')

        skel = "<progress data-value='/prop'></progress>"
        res = renderer.render('/', skel, mode="text")
        self.assertEqual(res, 'aBc')

        skel = "<progress data-value='prop%su'></progress>"
        res = renderer.render('/', skel, mode="text")
        self.assertEqual(res, 'ABC')

        skel = "<progress data-value='prop%sl'></progress>"
        res = renderer.render('/', skel, mode="text")
        self.assertEqual(res, 'abc')

        skel = "<progress data-value='prop%sc'></progress>"
        res = renderer.render('/', skel, mode="text")
        self.assertEqual(res, 'Abc')

        values = [{"data-path": "/", "prop": "020", "Id": 0}]
        js = json.dumps({"data-path": "/", "data-value": values})
        mock_studiogdo.get_list.return_value.content = js

        skel = "<progress data-value='prop'></progress>"
        res = renderer.render('/', skel, mode="text")
        self.assertEqual(res, '020')

        skel = "<progress data-value='prop%i'></progress>"
        res = renderer.render('/', skel, mode="text")
        self.assertEqual(res, '20')

        skel = "<progress data-value='prop%i*100'></progress>"
        res = renderer.render('/', skel, mode="text")
        self.assertEqual(res, '2000')

        skel = "<progress data-value='prop%i/20'></progress>"
        res = renderer.render('/', skel, mode="text")
        self.assertEqual(res, '1')

        skel = "<progress data-value='prop%i/100'></progress>"
        res = renderer.render('/', skel, mode="text")
        self.assertEqual(res, '0')

        skel = "<progress data-value='prop%i/100###'></progress>"
        res = renderer.render('/', skel, mode="text")
        self.assertEqual(res, '0.000')

        skel = "<progress data-value='prop%i/100,##'></progress>"
        res = renderer.render('/', skel, mode="text")
        self.assertEqual(res, '0,00')

        skel = u"<progress data-value='prop%i/100,##€'></progress>"
        res = renderer.render('/', skel, mode="text")
        self.assertEqual(res, u'0,00€')

        skel = u"<progress data-value='prop%i/100,## €'></progress>"
        res = renderer.render('/', skel, mode="text")
        self.assertEqual(res, u'0,00 €')

        skel = u"<progress data-value='prop%i/100,##%'></progress>"
        res = renderer.render('/', skel, mode="text")
        self.assertEqual(res, u'0,00%')

    @patch('studiogdo.api.StudiogdoApi')
    def test_renderer_post(self, mock_studiogdo):
        renderer = HTMLRenderer(mock_studiogdo, debug=True)

        values = [{"data-path": "/", "prop": "50", "Id": 0}]
        js = json.dumps({"data-path": "/", "data-value": values})
        mock_studiogdo.get_list.return_value.content = js
        skel = """<input data-value='prop'/>
            <input data-value='prop%s' name="s_"/>
            <input data-value='prop%i'/>
        """
        res = renderer.render('/', skel)
        self.assertRegexpMatches(res, '_L3Byb3A=')

    @patch('studiogdo.api.StudiogdoApi')
    def test_renderer_select(self, mock_studiogdo):
        """
        http://localhost:8080/morassuti/html/facet.gdo?p=/Services(baches)&f=python&m={%22data-path%22:%20%22Fixation%22,%20%22data-value%22:%20[%22Nom%22]}        """
        """
        {"data-path":"/Fixation","data-value":[{"data-path":"/Services(baches)/Fixation(1)","Nom":"Sans"},{"data-path":"/Services(baches)/Fixation(2)","Nom":"Colson/serflex blanc longueur 20cm"},{"data-path":"/Services(baches)/Fixation(3)","Nom":"Colson/serflex noir longueur 20cm"},{"data-path":"/Services(baches)/Fixation(4)","Nom":"Sandow/tendeur 1 crochets métal 20 cm"},{"data-path":"/Services(baches)/Fixation(5)","Nom":"Sandow/tendeur 1 crochets métal 40 cm"},{"data-path":"/Services(baches)/Fixation(6)","Nom":"Sandow/tendeur 2 crochets métal 20 cm"},{"data-path":"/Services(baches)/Fixation(7)","Nom":"Sandow/tendeur 2 crochets métal 40 cm"},{"data-path":"/Services(baches)/Fixation(8)","Nom":"Drisse polypro diam. 4 mm"},{"data-path":"/Services(baches)/Fixation(9)","Nom":"Drisse élastique diam. 8 mm"}]}    """
        renderer = HTMLRenderer(mock_studiogdo, debug=True)

        js1 = json.dumps({"data-path": "/", "data-value": [{"data-path": "/", "Nom": "Sans", "Id": 0}]})
        js2 = json.dumps({"data-path": "/Fixation", "Nom": "test", "data-value": [{"data-path": "/Fixation(0)", "Nom": "Sans", "Id": 0}, {"data-path": "/Fixation(1)", "Nom": "Colson/serflex blanc longueur 20cm", "Id": 1}, {"data-path": "/Fixation(2)", "Nom": "Colson/serflex noir longueur 20cm", "Id": 2}]})
        mock_studiogdo.get_list.side_effect = [HttpResponse(js1), HttpResponse(js2)]
        skel = """<select data-value='Nom'>
            <option data-path='Fixation' data-value='Nom' />
            </select>
        """
        res = renderer.render('/', skel)
        self.assertRegexpMatches(res, 'Colson/serflex blanc')
        self.assertRegexpMatches(res, 'Colson/serflex noir')
        self.assertRegexpMatches(res, 'selected="selected" value="Sans"')

        js1 = json.dumps({"data-path": "/", "data-value": [{"data-path": "/", "Nom": "Sans", "Id": "0"}]})
        js2 = json.dumps({"data-path": "/Fixation", "Nom": "test", "data-value": [{"data-path": "/Fixation(0)", "Nom": "Sans", "Id": "0"}, {"data-path": "/Fixation(1)", "Nom": "Colson/serflex blanc longueur 20cm", "Id": "1"}, {"data-path": "/Fixation(2)", "Nom": "Colson/serflex noir longueur 20cm", "Id": "2"}]})
        mock_studiogdo.get_list.side_effect = [HttpResponse(js1), HttpResponse(js2)]
        skel = """<select data-label='Nom'>
            <option data-path='Fixation' data-value='Id' data-label='Nom' />
            </select>
        """
        res = renderer.render('/', skel)
        self.assertRegexpMatches(res, 'selected="selected" value="0"')

        js1 = json.dumps({"data-path": "/", "data-value": [{"data-path": "/", "Nom": "Sans", "Id": "0"}]})
        js2 = json.dumps({"data-path": "/Fixation", "Nom": "test", "data-value": [{"data-path": "/Fixation(0)", "Nom": "Sans", "Id": "0"}, {"data-path": "/Fixation(1)", "Nom": "Colson/serflex blanc longueur 20cm", "Id": "1"}, {"data-path": "/Fixation(2)", "Nom": "Colson/serflex noir longueur 20cm", "Id": "2"}]})
        mock_studiogdo.get_list.side_effect = [HttpResponse(js1), HttpResponse(js2)]
        skel = """<select data-value='Nom'>
            <option value=''></option>
            <option value='1'></option>
            </select>
        """
        res = renderer.render('/', skel)
        self.assertRegexpMatches(res, 'option data-apath="Lw==" data-path-debug="/" value=""')

    @patch('studiogdo.api.StudiogdoApi')
    def test_renderer_ul(self, mock_studiogdo):
        renderer = HTMLRenderer(mock_studiogdo, debug=True)

        js1 = json.dumps({"data-path": "/", "data-value": [{"data-path": "/", "Nom": "Sans", "Id": "0"}]})
        js2 = json.dumps({"data-path": "/Fixation", "Nom": "test", "data-value": [{"data-path": "/Fixation(0)", "Nom": "Sans", "Id": "0"}, {"data-path": "/Fixation(1)", "Nom": "Colson/serflex blanc longueur 20cm", "Id": "1"}, {"data-path": "/Fixation(2)", "Nom": "Colson/serflex noir longueur 20cm", "Id": "2"}]})
        mock_studiogdo.get_list.side_effect = [HttpResponse(js1), HttpResponse(js2)]
        skel = """<ul data-cond='Nom'>
            <div data-value='Nom'></div>
            <li data-path='Fixation' data-value='Nom' />
            </ul>
        """
        res = renderer.render('/', skel)
        self.assertRegexpMatches(res, "Sans</span></li>")
        self.assertRegexpMatches(res, "Colson/serflex noir longueur 20cm</span></li></ul>")

        values = [{"data-path": "/", "prop": "test", "Id": "0"}]
        js = json.dumps({"data-path": "/", "data-value": values})
        mock_studiogdo.get_list.side_effect = [HttpResponse(js)]
        skel = """<ul><li>
            <p data-value="prop"></p>
        </li></ul>
        """
        res = renderer.render('/', skel)
        self.assertRegexpMatches(res, "test")

    @patch('studiogdo.api.StudiogdoApi')
    def test_renderer_table(self, mock_studiogdo):
        renderer = HTMLRenderer(mock_studiogdo, debug=True)

        js1 = json.dumps({"data-path": "/", "data-value": [{"Support": "Sans", "Id": "0", "data-path": "/Support"}]})
        js2 = json.dumps({"data-path": "/Support", "data-value": [{"Nom": "Sans", "Id": "0", "data-path": "Fixation(1)"}, {"Nom": "Colson/serflex blanc longueur 20cm", "Id": "1", "data-path": "Fixation(2)"}, {"Nom": "Colson/serflex noir longueur 20cm", "Id": "2", "data-path": "Fixation(3)"}]})
        mock_studiogdo.get_list.side_effect = [HttpResponse(js1), HttpResponse(js2)]
        skel = """<table data-path='Support'>
            <thead><tr data-path='Fixation'>
                <th data-value='Id' />
                <th data-value='Nom' />
            </tr></thead>
            </table>
        """

        res = renderer.render('/', skel)
        self.assertRegexpMatches(res, '<tbody>')
        self.assertRegexpMatches(res, '<td>0</td><td>Sans</td>')
        self.assertRegexpMatches(res, '<td>1</td><td>Colson/serflex blanc longueur 20cm</td>')

        js1 = json.dumps({"data-path": "/", "data-value": [{"Support": "Sans", "Id": "0", "data-path": "/Support"}]})
        js2 = json.dumps({"data-path": "/Support", "data-value": [{"Nom": "Sans", "Id": "0", "data-path": "Fixation(1)"}, {"Nom": "Colson/serflex blanc longueur 20cm", "Id": "1", "data-path": "Fixation(2)"}, {"Nom": "Colson/serflex noir longueur 20cm", "Id": "2", "data-path": "Fixation(3)"}]})
        mock_studiogdo.get_list.side_effect = [HttpResponse(js1), HttpResponse(js2)]
        skel = """<table>
            <caption data-value='Support'>
            </caption>
            <thead><tr data-path='Fixation'>
                <th data-value='Id' />
                <th data-value='Nom' />
            </tr></thead>
            </table>
        """

        res = renderer.render('/', skel)

    @patch('studiogdo.api.StudiogdoApi')
    def test_renderer_data(self, mock_studiogdo):
        renderer = HTMLRenderer(mock_studiogdo, debug=True)

        values = [{"data-path": "/", "prop": "50", "Id": 0}]
        js = json.dumps({"data-path": "/", "data-value": values})
        mock_studiogdo.get_list.return_value.content = js
        skel = """<input data-prop-test1='prop' test1='10'/>
            <input data-prop-test2='prop1' test2='10'/>
            <input data-prop+test3='prop' test3='10 30'/>
            <input data-text-test4='<span data-value="prop"/>' test4='10'/>
            <input data-text-test5='<span data-value="prop1"/>' test5='10'/>
            <input data-text+test6='<span data-value="prop"/>' test6='10 30'/>
            <input data-html='<span data-value="prop"/>' test7='10 30'/>
        """
        res = renderer.render('/', skel)
        self.assertRegexpMatches(res, 'test1="50"')
        self.assertRegexpMatches(res, 'test2="10"')
        self.assertRegexpMatches(res, 'test3="10 30 50"')
        self.assertRegexpMatches(res, 'test4="50"')
        self.assertRegexpMatches(res, 'test5="10"')
        self.assertRegexpMatches(res, 'test7="10 30"')
