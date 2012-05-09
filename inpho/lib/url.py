from urllib import FancyURLopener

class URLopener(FancyURLopener):
    """ URLopener with user-agent spoofing to test journal URLs. """
    # Reset user-agent header to Firefox 4 on OS X 10.6 (server config)
    version = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1)"
               "Gecko/20100101 Firefox/4.0.1")
