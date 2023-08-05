import time
from selenium import webdriver
from bs4 import BeautifulSoup


def get_browser_with_url(url, timeout=120, driver="firefox"):
    """Returns an open browser with a given url."""

    # choose a browser
    if driver == "firefox":
        browser = webdriver.Firefox()
    elif driver == "ie":
        browser = webdriver.Ie()
    elif driver == "chrome":
        browser = webdriver.Chrome()
    else:
        print "Driver choosen is not recognized"

    # set maximum load time
    browser.set_page_load_timeout(timeout)

    # open a browser with given url
    browser.get(url)

    time.sleep(5)

    return browser


def get_html_from_dynamic_site(url, timeout=120, driver="firefox", attempts=10):
    """Returns html from a dynamic site, opening it in a browser."""

    RV = ""

    # try several attempts
    for i in xrange(attempts):
        try:
            # load browser
            browser = get_browser_with_url(url, timeout, driver)

            # get html
            time.sleep(10)
            content = browser.page_source

            # try again if there is no content
            if not content:
                browser.quit()
                raise Exception("No content!")

            # if there is content gets out
            browser.quit()
            RV = content
            break

        except:
            print "\nTry ", i, " of ", attempts, "\n"
            time.sleep(5)

    return RV
