import argparse
import os
from bs4 import BeautifulSoup


def get_args():
    parser = argparse.ArgumentParser(description= "Static Site Generator - Reloader")
    parser.add_argument("root_directory", help="root directory of the files to serve")
    parser.add_argument("-i", "--ip", nargs="?", default="127.0.0.1", help="ip address on which to serve [127.0.0.1]")
    parser.add_argument("-p", "--port", nargs="?", type=int, default=5000, help="port on which to serve [5000]")
    parser.add_argument("-d", "--debug", action='store_true', help="Start Flask App in Debug mode")
    return parser.parse_args()

def watchdog_generator(path):
    #https://github.com/getpelican/pelican/blob/master/pelican/utils.py#L526
    def get_mtimes(path):
        for root, dirs, files in os.walk(path):
            for f in files:
                try:
                    yield os.stat(os.path.join(root, f)).st_mtime
                except OSError as e:
                    print ('Caught Exception: %s', e)
    LAST_MTIME = 0
    while True:
        try:
            mtime = max(get_mtimes(path))
            if mtime > LAST_MTIME:
                LAST_MTIME = mtime
                yield True
        except ValueError:
            yield None
        else:
            yield False

def inject_js(html_path):
    try:
        soup = BeautifulSoup(open(html_path), "html.parser")
        js_tag = soup.new_tag("script", type="text/javascript")
        js_tag.string = """function reloadRequest(){
                            var xhr = new XMLHttpRequest();
                            xhr.responseType = 'json';
                            xhr.timeout = 60000;
                            xhr.onload = function(e2){
                                var data = xhr.response;
                                if(data.reload){
                                    location.reload();
                                }
                                setTimeout(function(){ reloadRequest(); }, 1000);
                            }
                            xhr.ontimeout = function(){
                                //if you get this you probably should try to make the connection again.
                                //the browser should've killed the connection.
                                reloadRequest();
                            }
                            xhr.open('GET', "/_ssg_reloader", true);
                            xhr.send();
                        }
                        window.onload = reloadRequest;
                        """
        soup.body.append(js_tag)
        return soup.decode(formatter="html")
    except IOError as e:
        return "ioerror %s" % e
