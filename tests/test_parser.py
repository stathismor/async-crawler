from parser import Parser


def test_get_urls_full_urls():
    html = (
        "<title>Test page</title>"
        "<ul>"
        "  <li><a href='https://test.com/link_a'</a></li>"
        "  <li><a href='https://test.com/link_b'</a></li>"
        "</ul>"
    )
    url = "https://test.com/"
    subdomain = "test.com"

    parser = Parser(html, url, subdomain)
    assert parser.get_urls() == {"https://test.com/link_a", "https://test.com/link_b"}


def test_get_urls_different_subdomain():
    html = (
        "<title>Test page</title>"
        "<ul>"
        "  <li><a href='https://test.com/link_a'</a></li>"
        "  <li><a href='https://another.domain.test.com/link_b'</a></li>"
        "</ul>"
    )
    url = "https://test.com/"
    subdomain = "test.com"

    parser = Parser(html, url, subdomain)
    assert parser.get_urls() == {"https://test.com/link_a"}


def test_get_urls_trailing_slash():
    html = "<title>Test page</title><a href='/link_b'</a></li>"
    url = "https://test.com/link_a"
    subdomain = "test.com"

    parser = Parser(html, url, subdomain)
    print(parser.get_urls())
    assert parser.get_urls() == {"https://test.com/link_b"}


def test_get_urls_relative_urls():
    html = (
        "<title>Test page</title>"
        "<ul>"
        "  <li><a href='link_b'</a></li>"
        "  <li><a href='link_c/link_d'</a></li>"
        "</ul>"
    )
    url = "https://test.com/link_a/"
    subdomain = "test.com"

    parser = Parser(html, url, subdomain)
    assert parser.get_urls() == {
        "https://test.com/link_a/link_b",
        "https://test.com/link_a/link_c/link_d",
    }


def test_get_urls_external_urls():
    html = (
        "<title>Test page</title>"
        "<ul>"
        "  <li><a href='https://external.com/link_a'</a></li>"
        "  <li><a href='http://external.domain.com/link_b'</a></li>"
        "</ul>"
    )
    url = "https://test.com/link_a/"
    subdomain = "test.com"

    parser = Parser(html, url, subdomain)
    assert parser.get_urls() == set()
