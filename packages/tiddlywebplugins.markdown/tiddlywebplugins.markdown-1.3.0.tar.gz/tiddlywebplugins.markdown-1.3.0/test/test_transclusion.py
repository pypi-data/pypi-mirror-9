import shutil
import pytest

from tiddlywebplugins.markdown import render
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.config import config
from tiddlyweb.web.util import tiddler_url

from tiddlywebplugins.utils import get_store


environ = {
    'tiddlyweb.config': {
        'markdown.wiki_link_base': '',
        'wikitext.type_render_map': {
            'text/x-markdown': 'tiddlywebplugins.markdown'
        },
        'server_host': {
            'scheme': 'http',
            'host': 'tiddlyspace.com',
            'port': '80'
        }
    },
    'tiddlyweb.usersign': {
        'name': 'GUEST',
        'roles': []
    },
    # get friendly urls doing their thing
    'wsgi.url_scheme': 'http'
}

try:
    import tiddlywebplugins.tiddlyspace
    tiddlyspace = True
except ImportError:
    tiddlyspace = False


def setup_module(module):
    try:
        shutil.rmtree('store')
    except:
        pass
    config['markdown.wiki_link_base'] = ''
    store = get_store(config)

    environ['tiddlyweb.store'] = store

    store.put(Bag('bag_public'))
    module.store = store

    recipe = Recipe('recipe_public')
    recipe.set_recipe([('bag_public', '')])
    store.put(recipe)

    tiddlerA = Tiddler('tiddler a', 'bag_public')
    tiddlerA.text = 'I am _tiddler_'
    tiddlerA.type = 'text/x-markdown'
    store.put(tiddlerA)

    tiddlerB = Tiddler('tiddler b')
    tiddlerB.text = '''
You wish

{{tiddler a}}

And I wish too.
'''
    module.tiddlerB = tiddlerB

    store.put(Bag('spaced bag'))
    tiddlerX = Tiddler('tiddler x', 'spaced bag')
    tiddlerX.text = 'X is not Y'
    tiddlerX.type = 'text/x-markdown'
    store.put(tiddlerX)


def test_no_bag():
    output = render(tiddlerB, environ)

    assert 'I am <em>tiddler</em>' not in output
    assert 'You wish' in output


def test_recipe():
    tiddlerB.recipe = 'recipe_public'
    output = render(tiddlerB, environ)

    assert 'I am <em>tiddler</em>' in output
    assert 'You wish' in output


def test_bag():
    output = render(tiddlerB, environ)
    tiddlerB.bag = 'bag_public'

    assert 'I am <em>tiddler</em>' in output
    assert 'You wish' in output


def test_double_render_transclude():
    tiddlerA = store.get(Tiddler('tiddler a', 'bag_public'))
    tiddlerA.type = 'text/x-markdown'
    store.put(tiddlerA)

    output = render(tiddlerB, environ)

    assert 'I am <em>tiddler</em>' in output
    assert 'You wish' in output


def test_spaced_target_include():
    def target_resolver(environ, target, interior_tiddler):
        interior_tiddler.bag = target
    environ['tiddlyweb.config']['markdown.transclude_url'] = tiddler_url
    environ['tiddlyweb.config']['markdown.target_resolver'] = target_resolver
    tiddlerB.text = '''
Hey There

{{tiddler x}}@[[spaced bag]]

We called that from outside, yo, and we'll call it again.

{{tiddler x}}@[[spaced bag]]

{{tiddler a}}@bag_public
'''

    output = render(tiddlerB, environ)

# Note: the URI here is funkity because of the above config settings
    assert '<article id="t-tiddler-x" class="transclusion" data-uri="http://tiddlyspace.com/bags/spaced%20bag/tiddlers/tiddler%20x" data-title="tiddler x" ' \
            'data-bag="spaced bag"><p>X is not Y</p></article>' in output
    assert 'We called that from outside,' in output
    assert 'I am <em>tiddler</em>' in output


@pytest.mark.skipif('tiddlyspace == False')
def test_space_include():
    from tiddlywebplugins.markdown.transclusion import tiddlyspace_target_resolver
    from tiddlywebplugins.tiddlyspace.fixups import web_tiddler_url as tu
    def tiddler_url(environ, tiddler):
        return tu(environ, tiddler, friendly=True)
    environ['tiddlyweb.config']['markdown.transclude_url'] = tiddler_url
    environ['tiddlyweb.config']['markdown.target_resolver'] = tiddlyspace_target_resolver
    tiddlerB.text = '''
Hey There

{{tiddler a}}@recipe

We called that from outside, yo, and we'll call it again.

{{tiddler a}}@recipe
'''

    output = render(tiddlerB, environ)

# Note: the URI here is funkity because of the above config settings
    assert '<article id="t-tiddler-a" class="transclusion" data-uri="http://bag.tiddlyspace.com/tiddler%20a" data-title="tiddler a" ' \
            'data-bag="bag_public"><p>I am <em>tiddler</em></p></article>' in output
    assert 'We called that from outside,' in output
