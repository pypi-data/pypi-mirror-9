from dragline.http import Request
from dragline.parser import HtmlParser
import argparse
from lxml.html import open_in_browser
from collections import defaultdict
import traceback


def start_python_console(namespace=None, noipython=False, banner=''):
    """Start Python console binded to the given namespace. If IPython is
    available, an IPython console will be started instead, unless `noipython`
    is True. Also, tab completion will be used on Unix systems.
    """
    if namespace is None:
        namespace = {}

    try:
        try:  # use IPython if available
            if noipython:
                raise ImportError()
            try:
                try:
                    from IPython.terminal import embed
                except ImportError:
                    from IPython.frontend.terminal import embed
                sh = embed.InteractiveShellEmbed(banner1=banner)
            except ImportError:
                from IPython.Shell import IPShellEmbed
                sh = IPShellEmbed(banner=banner)
            sh(global_ns={}, local_ns=namespace)
        except ImportError:
            import code
            try:  # readline module is only available on unix systems
                import readline
            except ImportError:
                pass
            else:
                import rlcompleter
                readline.parse_and_bind("tab:complete")
            code.interact(banner=banner, local=namespace)
    except SystemExit:  # raised when using exit() in python code.interact
        pass


def help():
    repr_data = defaultdict(lambda: None, {k: repr(v) for k, v in data.iteritems()})
    intro = """\n[d] Available Dragline objects:
    [d]   parser                 %(parser)s
    [d]   request                %(request)s
    [d]   response               %(response)s
    [d] Useful shortcuts: ## Override methods in Cmd object ##
    [d]   shelp()                Shell help (print this help)
    [d]   fetch(req_or_url)      Fetch request (or URL) and update local objects
    [d]   view(response=None)    View response in a browser\n\n""" % repr_data
    return intro


def process(req_or_url):
    global data
    if not req_or_url:
        return help()
    if isinstance(req_or_url, Request):
        data["request"] = req_or_url
    else:
        data["request"] = Request(req_or_url)
    try:
        data["response"] = data["request"].send()
    except:
        data["response"] = None
        print traceback.format_exc()
        print("Failed to fetch")
    try:
        data["parser"] = HtmlParser(data["response"])
    except:
        data["parser"] = None
        print("Failed to parse response")
    return help()


def fetch(req_or_url):
    result = process(req_or_url)
    print result


def view(response=None):
    if response is None:
        global data
        response = data["response"]
    open_in_browser(HtmlParser(response), response.encoding)

data = {"fetch": fetch, "view": view, "shelp": help,
        "Request": Request, 'parser': None, 'response': None,
        'request': None}


def execute():
    parser = argparse.ArgumentParser()
    parser.add_argument('url', action='store', default='', help='url', nargs='?')
    url = (parser.parse_args()).url
    result = process(url)
    start_python_console(data, banner=result)


if __name__ == "__main__":
    execute()
