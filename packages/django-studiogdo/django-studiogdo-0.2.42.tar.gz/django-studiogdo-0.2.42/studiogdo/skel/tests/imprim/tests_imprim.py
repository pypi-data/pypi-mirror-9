# -*- coding: utf-8 -*-

import json
import codecs

from django.test import TestCase
from mock import patch

from studiogdo.skel.renderer import HTMLRenderer


class Test(TestCase):
    @patch('studiogdo.api.StudiogdoApi')
    def test_cart(self, mock_studiogdo):
        renderer = HTMLRenderer(mock_studiogdo, debug=True)

        values = {"data-path": "/", "TelephoneContact": "tel_contact", "PrenomContact": "prenom_contact",
                   "Adresse1Liv": "adresse1_liv", "PaysLiv": "pays_liv",
                   "NomContact": "nom_contact", "EmailContact": "email_contact",
                   "Id": 0}
        js = json.dumps(values)
        mock_studiogdo.get_list.return_value.content = js
        with open('studiogdo/skel/tests/imprim/cart.skel', 'r') as content_file:
            skel = content_file.read()
        res = renderer.render('/', skel)
        with codecs.open('studiogdo/skel/tests/imprim/cart.res', 'r', 'UTF-8') as result_file:
            fres = result_file.read()
        self.assertListEqual(res.split('\n'), fres.split('\n'))

