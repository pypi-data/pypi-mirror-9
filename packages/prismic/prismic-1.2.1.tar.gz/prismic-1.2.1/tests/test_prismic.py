#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for Prismic library"""

from __future__ import (absolute_import, division, print_function, unicode_literals)

from prismic.cache import ShelveCache
from prismic.exceptions import InvalidTokenError, AuthorizationNeededError, InvalidURLError
from .test_prismic_fixtures import fixture_api, fixture_search, fixture_groups, \
    fixture_structured_lists, fixture_empty_paragraph, fixture_store_geopoint, \
    fixture_image_links, fixture_spans_labels, fixture_block_labels, fixture_custom_html
import time
import json
import logging
import prismic
from prismic import predicates
import unittest

# logging.basicConfig(level=logging.DEBUG)
# log = logging.getLogger(__name__)


class PrismicTestCase(unittest.TestCase):
    def setUp(self):
        """Init the api url and the token identifier."""
        self.api_url = "http://lesbonneschoses.prismic.io/api"
        self.token = "MC5VZ2phOGRfbXFaOEl2UEpj.dO-_ve-_ve-_ve-_vSFRBzXvv71V77-977-9BO-_vVbvv71k77-9Cu-_ve-_vQTvv71177-9eQpcUE3vv70"
        self.fixture_api = json.loads(fixture_api)
        self.fixture_search = json.loads(fixture_search)
        self.fixture_structured_lists = json.loads(fixture_structured_lists)
        self.fixture_empty_paragraph = json.loads(fixture_empty_paragraph)
        self.fixture_block_labels = json.loads(fixture_block_labels)
        self.fixture_store_geopoint = json.loads(fixture_store_geopoint)
        self.fixture_groups = json.loads(fixture_groups)
        self.fixture_image_links = json.loads(fixture_image_links)
        self.fixture_spans_labels = json.loads(fixture_spans_labels)
        self.fixture_custom_html = json.loads(fixture_custom_html)

        self.api = prismic.Api(self.fixture_api, self.token, ShelveCache("prismictest"), None)

    def tearDown(self):
        """Teardown."""

    @staticmethod
    def link_resolver(document_link):
        if document_link.is_broken:
            return "#broken"
        else:
            return "/document/%s/%s" % (document_link.id, document_link.slug)

    @staticmethod
    def html_serializer(element, content):
        if isinstance(element, prismic.fragments.Block.Image):
            return element.get_view().as_html(PrismicTestCase.link_resolver)
        if isinstance(element, prismic.fragments.Span.Hyperlink):
            return """<a class="some-link" href="%s">""" % element.get_url(PrismicTestCase.link_resolver) + content + "</a>"
        return None


class ApiIntegrationTestCase(PrismicTestCase):
    """Doing real HTTP requests to test API data fetching"""

    def setUp(self):
        super(ApiIntegrationTestCase, self).setUp()
        self.api = prismic.get(self.api_url, self.token)

    def test_get_api(self):
        self.assertTrue(len(self.api.forms) > 0)

    def test_api_get_errors(self):
        with self.assertRaises(InvalidTokenError):
            prismic.get(self.api_url, "wrong")

        with self.assertRaises(AuthorizationNeededError):
            prismic.get(self.api_url, "")

        with self.assertRaises(InvalidURLError):
            prismic.get("htt://wrong_on_purpose", "")

    def test_search_form(self):
        blog = self.api.form("blog")
        blog.ref(self.api.get_master())
        docs = blog.submit().documents
        self.assertEqual(len(docs), 6)
        self.assertEqual(docs[0].type, "blog-post")

    def test_search_form_orderings(self):
        blog = self.api.form("blog")
        blog.ref(self.api.get_master())
        blog.orderings("""[my.blog-post.date]""")
        docs = blog.submit().documents
        self.assertEqual(docs[0].slug, 'les-bonnes-chosess-internship-a-testimony')
        self.assertEqual(docs[1].slug, 'get-the-right-approach-to-ganache')

    def test_search_form_page_size(self):
        blog = self.api.form("blog").page_size(2)
        blog.ref(self.api.get_master())
        response = blog.submit()
        self.assertEqual(len(response.documents), 2)
        self.assertEqual(response.results_per_page, 2)

    def test_search_form_first_page(self):
        blog = self.api.form("blog").pageSize(4)
        blog.ref(self.api.get_master())
        response = blog.submit()
        self.assertEqual(response.page, 1)
        self.assertEqual(len(response.documents), 4)
        self.assertEqual(response.results_size, len(response.documents))
        self.assertIsNone(response.prev_page)
        self.assertEqual(response.next_page,
                         'http://lesbonneschoses.prismic.io/api/documents/search?ref=UlfoxUnM08QWYXdl&q=%5B%5B%3Ad+%3D+any%28document.type%2C+%5B%22blog-post%22%5D%29%5D%5D&page=2&pageSize=4')

    def test_search_form_last_page(self):
        blog = self.api.form("blog").pageSize(4).page(2)
        blog.ref(self.api.get_master())
        response = blog.submit()
        self.assertEqual(response.page, 2)
        self.assertEqual(len(response.documents), 2)
        self.assertEqual(response.results_size, len(response.documents))
        self.assertIsNone(response.next_page)
        self.assertEqual(response.prev_page,
                         'http://lesbonneschoses.prismic.io/api/documents/search?ref=UlfoxUnM08QWYXdl&q=%5B%5B%3Ad+%3D+any%28document.type%2C+%5B%22blog-post%22%5D%29%5D%5D&page=1&pageSize=4')

    def test_search_form_count(self):
        blog = self.api.form("blog")
        blog.ref(self.api.get_master())
        nb_docs = blog.count()
        self.assertEqual(nb_docs, 6)

    def test_linked_documents(self):
        gift_box = self.api\
            .form("everything")\
            .ref(self.api.get_master())\
            .query("[[:d = at(document.id, \"UlfoxUnM0wkXYXbZ\")]]")\
            .submit()\
            .documents[0]
        linked = gift_box.linked_documents
        self.assertEqual(len(linked), 3)

    def test_fetch_links(self):
        article = self.api\
            .form('everything')\
            .ref(self.api.get_master())\
            .fetch_links('blog-post.author')\
            .query(predicates.at('document.id', 'UlfoxUnM0wkXYXbt')) \
            .submit()\
            .documents[0]
        links = article.get_all('blog-post.relatedpost')
        self.assertEqual(links[0].get_text('blog-post.author'), 'John M. Martelle, Fine Pastry Magazine')

    def test_fetch_links_list(self):
        article = self.api\
            .form('everything')\
            .ref(self.api.get_master())\
            .fetch_links(['blog-post.author', 'blog-post.title'])\
            .query(predicates.at('document.id', 'UlfoxUnM0wkXYXbt')) \
            .submit()\
            .documents[0]
        links = article.get_all('blog-post.relatedpost')
        self.assertEqual(links[0].get_text('blog-post.author'), 'John M. Martelle, Fine Pastry Magazine')


class ApiTestCase(PrismicTestCase):
    def test_get_ref(self):
        self.assertTrue(self.api.get_ref("Master").ref == "UgjWQN_mqa8HvPJY")

    def test_master(self):
        self.assertTrue(self.api.get_master().ref == "UgjWQN_mqa8HvPJY")
        self.assertTrue(self.api.get_master().id == "master")


class TestSearchFormTestCase(PrismicTestCase):
    def test_document(self):
        docs = [prismic.Document(doc) for doc in self.fixture_search]
        self.assertTrue(len(docs) == 3)
        doc = docs[0]
        self.assertTrue(doc.slug == "vanilla-macaron")

    def test_empty_slug(self):
        doc_json = self.fixture_search[0]
        doc_json["slugs"] = None
        doc = prismic.Document(doc_json)
        self.assertTrue(doc.slug == "-")

    def test_as_html(self):
        doc_json = self.fixture_search[0]
        doc = prismic.Document(doc_json)
        expected_html = """<section data-field="product.allergens"><span class="text">Contains almonds, eggs, milk</span></section><section data-field="product.image"><img src="https://wroomio.s3.amazonaws.com/lesbonneschoses/0417110ebf2dc34a3e8b7b28ee4e06ac82473b70.png" width="500" height="500"></section><section data-field="product.short_lede"><h2>Crispiness and softness, rolled into one</h2></section><section data-field="product.testimonial_author[0]"><h3>Chef Guillaume Bort</h3></section><section data-field="product.related[0]"><a href="document/UdUjvt_mqVNObPeO">dark-chocolate-macaron</a></section><section data-field="product.name"><h1>Vanilla Macaron</h1></section><section data-field="product.related[1]"><a href="document/UdUjsN_mqT1ObPeM">salted-caramel-macaron</a></section><section data-field="product.testimonial_quote[0]"><p>The taste of pure vanilla is very hard to tame, and therefore, most cooks resort to substitutes. <strong>It takes a high-skill chef to know how to get the best of tastes, and <strong><em></strong>Les Bonnes Choses<strong></em></strong>'s vanilla macaron does just that</strong>. The result is more than a success, it simply is a gastronomic piece of art.</p></section><section data-field="product.flavour[0]"><span class="text">Vanilla</span></section><section data-field="product.price"><span class="number">3.55</span></section><section data-field="product.color"><span class="color">#ffeacd</span></section><section data-field="product.description"><p>Experience the ultimate vanilla experience. Our vanilla Macarons are made with our very own (in-house) <strong>pure extract of Madagascar vanilla</strong>, and subtly dusted with <strong>our own vanilla sugar</strong> (which we make from real vanilla beans).</p></section>"""
        doc_html = doc.as_html(lambda link_doc: "document/%s" % link_doc.id)
        # Comparing len rather than actual strings because json loading is not in a deterministic order for now
        self.assertEqual(len(expected_html), len(doc_html))

    def test_default_params(self):
        blog = self.api.form("blog")
        self.assertEqual(len(blog.data), 1)
        self.assertEqual(blog.data["q"], ["[[any(document.type, [\"blog-post\"])]]"])

    def test_query_append_value(self):
        blog = self.api.form("blog")
        blog.query("[[bar]]")
        self.assertEqual(len(blog.data), 1)
        self.assertEqual(blog.data["q"], ["[[any(document.type, [\"blog-post\"])]]", "[[bar]]"])

    def test_ref_replace_value(self):
        blog = self.api.form("blog")
        blog.ref("foo")
        self.assertEqual(len(blog.data), 2)
        self.assertEqual(blog.data["ref"], "foo")
        blog.ref("bar")
        self.assertEqual(len(blog.data), 2)
        self.assertEqual(blog.data["ref"], "bar")

    def test_set_page_size(self):
        blog = self.api.form("blog")
        blog.page_size(3)
        self.assertEqual(len(blog.data), 2)
        self.assertEqual(blog.data["pageSize"], 3)

    def test_set_page(self):
        blog = self.api.form("blog")
        blog.page(3)
        self.assertEqual(len(blog.data), 2)
        self.assertEqual(blog.data["page"], 3)


class TestFragmentsTestCase(PrismicTestCase):
    def setUp(self):
        super(TestFragmentsTestCase, self).setUp()
        doc_json = self.fixture_search[0]
        self.doc = prismic.Document(doc_json)

    def test_image(self):
        doc = self.doc
        self.assertEqual(doc.get_image("product.image", "main").width, 500)
        self.assertEqual(doc.get_image("product.image", "icon").width, 250)
        expected_html = \
            ("""<img """
             """src="https://wroomio.s3.amazonaws.com/lesbonneschoses/babdc3421037f9af77720d8f5dcf1b84c912c6ba.png" """
             """width="250" height="250">""")
        self.assertEqual(expected_html, doc.get_image("product.image", "icon").as_html(PrismicTestCase.link_resolver))

    def test_number(self):
        doc = self.doc
        self.assertEqual(doc.get_number("product.price").__str__(), "3.55")

    def test_color(self):
        doc = self.doc
        self.assertEqual(doc.get_color("product.color").__str__(), "#ffeacd")

    def test_text(self):
        doc = self.doc
        self.assertEqual(doc.get_text("product.allergens").__str__(), "Contains almonds, eggs, milk")

        text = prismic.Fragment.Text("a&b 42 > 41")
        self.assertEqual(text.as_html, '<span class="text">a&amp;b 42 &gt; 41</span>', "HTML escape")

    def test_structured_text_heading(self):
        doc = self.doc
        html = doc.get_html("product.short_lede", lambda x: "/x")
        self.assertEqual("<h2>Crispiness and softness, rolled into one</h2>", html)

    def test_structured_text_paragraph(self):
        span_sample_data = {"type": "paragraph",
                            "text": "To be or not to be ?",
                            "spans": [
                                {"start": 3, "end": 5, "type": "strong"},
                                {"start": 16, "end": 18, "type": "strong"},
                                {"start": 3, "end": 5, "type": "em"}
                            ]}
        p = prismic.fragments.StructuredText([span_sample_data])
        p_html = p.as_html(lambda x: "/x")
        self.assertEqual(p_html, "<p>To <em><strong>be</strong></em> or not to <strong>be</strong> ?</p>")

        p = prismic.fragments.StructuredText([{"type": "paragraph", "text": "a&b 42 > 41", "spans": []}])
        p_html = p.as_html(lambda x: "/x")
        self.assertEqual(p_html, "<p>a&amp;b 42 &gt; 41</p>", "Paragraph HTML escape")

        p = prismic.fragments.StructuredText([{"type": "heading2", "text": "a&b 42 > 41", "spans": []}])
        p_html = p.as_html(lambda x: "/x")
        self.assertEqual(p_html, "<h2>a&amp;b 42 &gt; 41</h2>", "Header HTML escape")

    def test_spans(self):
        doc_json = self.fixture_spans_labels
        p = prismic.fragments.StructuredText(doc_json.get("value"))
        p_html = p.as_html(lambda x: "/x")
        self.assertEqual(p_html, ("""<p>Two <strong><em>spans</em> with</strong> the same start</p>"""
                                  """<p>Two <em><strong>spans</strong> with</em> the same start</p>"""
                                  """<p>Span till the <span class="tip">end</span></p>"""))

    def test_lists(self):
        doc_json = self.fixture_structured_lists[0]
        doc = prismic.Document(doc_json)
        doc_html = doc.get_structured_text("article.content").as_html(lambda x: "/x")
        expected = ("""<h2>A tale of pastry and passion</h2>"""
                    """<h2>Here we'll test a list</h2>"""
                    """<p>Unordered list:</p>"""
                    """<ul><li>Element1</li><li>Element2</li><li>Element3</li></ul>"""
                    """<p>Ordered list:</p><ol><li>Element1</li><li>Element2</li><li>Element3</li></ol>""")
        self.assertEqual(doc_html, expected)

    def test_empty_paragraph(self):
        doc_json = self.fixture_empty_paragraph
        doc = prismic.Document(doc_json)

        doc_html = doc.get_field('announcement.content').as_html(PrismicTestCase.link_resolver)
        expected = """<p>X</p><p></p><p>Y</p>"""
        self.assertEqual(doc_html, expected)

    def test_block_labels(self):
        doc_json = self.fixture_block_labels
        doc = prismic.Document(doc_json)

        doc_html = doc.get_field('announcement.content').as_html(PrismicTestCase.link_resolver)
        expected = """<p class="code">some code</p>"""
        self.assertEqual(doc_html, expected)

    def test_get_text(self):
        doc_json = self.fixture_search[0]
        doc = prismic.Document(doc_json)
        self.assertEqual(doc.get_text('product.description'), 'Experience the ultimate vanilla experience. Our vanilla Macarons are made with our very own (in-house) pure extract of Madagascar vanilla, and subtly dusted with our own vanilla sugar (which we make from real vanilla beans).')

    def test_document_link(self):
        test_paragraph = {
            "type": "paragraph",
            "text": "bye",
            "spans": [
                {
                    "start": 0,
                    "end": 3,
                    "type": "hyperlink",
                    "data": {
                        "type": "Link.document",
                        "value": {
                            "document": {
                                "id": "UbiYbN_mqXkBOgE2", "type": "article", "tags": ["blog"], "slug": "-"
                            },
                            "isBroken": False
                        }
                    }
                },
                {"start": 0, "end": 3, "type": "strong"}
            ]
        }
        p = prismic.fragments.StructuredText([test_paragraph])

        def link_resolver(document_link):
            return "/document/%s/%s" % (document_link.id, document_link.slug)

        p_html = p.as_html(link_resolver)
        self.assertEqual(p_html, """<p><strong><a href="/document/UbiYbN_mqXkBOgE2/-">bye</a></strong></p>""")

    def test_geo_point(self):
        store = prismic.Document(self.fixture_store_geopoint)
        geopoint = store.get_field("store.coordinates")
        self.assertEqual(geopoint.as_html,
                         ("""<div class="geopoint"><span class="latitude">37.777431</span>"""
                          """<span class="longitude">-122.415419</span></div>"""))

    def test_group(self):
        contributor = prismic.Document(self.fixture_groups)
        links = contributor.get_group("contributor.links")
        self.assertEquals(len(links.value), 2)

    def test_image_links(self):
        self.maxDiff = 10000
        text = prismic.fragments.StructuredText(self.fixture_image_links.get('value'))

        self.assertEqual(
            text.as_html(PrismicTestCase.link_resolver),
            ('<p>Here is some introductory text.</p>'
             '<p>The following image is linked.</p>'
             '<p class=\"block-img\"><a href=\"http://google.com/\">'
             '<img src=\"http://fpoimg.com/129x260\" width=\"260\" height=\"129\"></a></p>'
             '<p><strong>More important stuff</strong></p><p>The next is linked to a valid document:</p>'
             '<p class=\"block-img\"><a href=\"/document/UxCQFFFFFFFaaYAH/something-fantastic\">'
             '<img src=\"http://fpoimg.com/400x400\" width=\"400\" height=\"400\"></a></p>'
             '<p>The next is linked to a broken document:</p><p class=\"block-img\"><a href=\"#broken\">'
             '<img src=\"http://fpoimg.com/250x250\" width=\"250\" height=\"250\"></a></p>'
             '<p>One more image, this one is not linked:</p><p class=\"block-img\">'
             '<img src=\"http://fpoimg.com/199x300\" width=\"300\" height=\"199\"></p>'))

    def test_custom_html(self):
        self.maxDiff = 10000
        text = prismic.fragments.StructuredText(self.fixture_custom_html.get('value'))

        self.assertEqual(
            text.as_html(PrismicTestCase.link_resolver, PrismicTestCase.html_serializer),
            ('<p>Here is some introductory text.</p>'
             '<p>The following image is linked.</p>'
             '<a href=\"http://google.com/\"><img src=\"http://fpoimg.com/129x260\" width=\"260\" height=\"129\"></a>'
             '<p><strong>More important stuff</strong></p><p>The next is linked to a valid document:</p>'
             '<a href=\"/document/UxCQFFFFFFFaaYAH/something-fantastic\">'
             '<img src=\"http://fpoimg.com/400x400\" width=\"400\" height=\"400\"></a>'
             '<p>The next is linked to a broken document:</p><a href=\"#broken\">'
             '<img src=\"http://fpoimg.com/250x250\" width=\"250\" height=\"250\"></a>'
             '<p>One more image, this one is not linked:</p>'
             '<img src=\"http://fpoimg.com/199x300\" width=\"300\" height=\"199\">'
             '<p>This <a class="some-link" href="/document/UlfoxUnM0wkXYXbu/les-bonnes-chosess-internship-a-testimony">'
             'paragraph</a> contains an hyperlink.</p>'))


class PredicatesTestCase(PrismicTestCase):

    def test_at(self):
        f = self.api\
            .form("everything")\
            .ref(self.api.get_master())\
            .query(predicates.at('document.id', 'UlfoxUnM0wkXYXbZ'))
        self.assertEqual(f.data['q'], ["[[:d = at(document.id, \"UlfoxUnM0wkXYXbZ\")]]"])

    def test_any(self):
        f = self.api \
            .form("everything") \
            .ref(self.api.get_master()) \
            .query(predicates.any('document.type', ['article', 'blog-post']))
        self.assertEqual(f.data['q'], ['[[:d = any(document.type, ["article", "blog-post"])]]'])

    def test_similar(self):
        f = self.api \
            .form("everything") \
            .ref(self.api.get_master()) \
            .query(predicates.similar('idOfSomeDocument', 10))
        self.assertEqual(f.data['q'], ['[[:d = similar("idOfSomeDocument", 10)]]'])

    def test_multiple_predicates(self):
        f = self.api \
            .form("everything") \
            .ref(self.api.get_master()) \
            .query(
                predicates.month_after('my.blog-post.publication-date', 4),
                predicates.month_before('my.blog-post.publication-date', 'December')
            )
        self.assertEqual(f.data['q'], ['[[:d = date.month-after(my.blog-post.publication-date, 4)][:d = date.month-before(my.blog-post.publication-date, "December")]]'])

    def test_number_lt(self):
        f = self.api \
            .form("everything") \
            .ref(self.api.get_master()) \
            .query(predicates.lt('my.blog-post.publication-date', 4))
        self.assertEqual(f.data['q'], ['[[:d = number.lt(my.blog-post.publication-date, 4)]]'])

    def test_number_in_range(self):
        f = self.api \
            .form("everything") \
            .ref(self.api.get_master()) \
            .query(predicates.in_range('my.product.price', 2, 4.5))
        self.assertEqual(f.data['q'], ['[[:d = number.inRange(my.product.price, 2, 4.5)]]'])

    def test_geopoint_near(self):
        f = self.api \
            .form("everything") \
            .ref(self.api.get_master()) \
            .query(predicates.near('my.store.coordinates', 40.689757, -74.0451453, 15))
        self.assertEqual(f.data['q'], ['[[:d = geopoint.near(my.store.coordinates, 40.689757, -74.0451453, 15)]]'])


class TestCache(unittest.TestCase):

    def setUp(self):
        self.cache = ShelveCache("cachetest")

    def test_set_get(self):
        self.cache.set("foo", "bar", 3600)
        self.assertEqual(self.cache.get("foo"), "bar")

    def test_expiration(self):
        self.cache.set("toto", "tata", 2)
        time.sleep(3)
        self.assertIsNone(self.cache.get("toto"))


if __name__ == '__main__':
    unittest.main()

