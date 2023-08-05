from mediagenie.bundle import Bundle
from nose.tools import raises

BUNDLE = ('foo.css', 'css/one.css', 'css/two.css', 'css/four.scss')
bundle = Bundle(BUNDLE)

def test_bundle_init():
    
    assert bundle.name == 'foo.css'
    assert len(bundle.files) == 3

@raises(ValueError)
def test_bundle_bad_init():
    BAD_BUNDLE = ('foo.css',)
    bundle = Bundle(BAD_BUNDLE)

def test_bundle_data():
    assert len(list(bundle.data())) == 3
