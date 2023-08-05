import logging

logging.basicConfig(level=logging.DEBUG)

import plotly.tools as tls
import base64
from IPython.display import HTML, display, clear_output, Javascript, clear_output
import plotly.plotly as py
import uuid
import threading
import time
import uuid
import json
from pkg_resources import resource_string


class CachedPlot():
    def __init__(self):
        self.image_js = ''
        self.png = ''
        self.plot_js = ''
        self.container_id = str(uuid.uuid4())
        self.image_failed = False

        # inject css
        css = resource_string('plotly', 'plotly/displayCSS.html').decode('utf-8')
        HTML(css)
        # other requirements
        unveil = resource_string('plotly', 'plotly/jquery.unveil.js').decode('utf-8')
        html_unveil_script = '<script type="text/javascript">console.log("js unveil code");' + unveil + '</script>'
        display(HTML(html_unveil_script))

    def container_html(self):

        js_display_code = resource_string('plotly',
                                          'plotly/displayLogic.js').decode('utf-8')

        html = ('<div class="plotly-output-container" id="'+self.container_id+'">'
                    '<div class="loading"></div>'
                    '<div class="toggle"></div>'
                '</div>'
                '<script type="text/javascript">console.log("js_display_code");' + '$(\'.plotly-output-container\').unveil(500);' + '</script>')
        # '<script type="text/javascript">$(document).ready(function(){console.log("on document load"); window.displayLogic(\''+self.container_id+'\');});</script>'
        return html


    def image_code(self):
        js = ('console.log("image code");'
            'var $container = $(\'#{container_id}\');'
            '$container.prepend(\'<img style="width:1000px;" src="{src}">\');');
        js = js.format(src='data:image/png;base64,'+base64.b64encode(self.png), container_id=self.container_id)
        self.image_js = js

    def gen_image(self, figure_or_data):
        try:
            self.png = py.image.get(figure_or_data, format='png', width=1000, height=600)
        except:
            self.image_failed = True


    def iframe_code(self, figure_or_data):
        js = ('console.log("iframe code");'
            'var $container = $("#{container_id}");'
            '$container.prepend(\'<iframe scrolling="no" style="border:none;"seamless="seamless" display:none; data-src="{url}.embed" height="600" width="100%"> </iframe>\');');

        url = py.plot(figure_or_data, filename=self.container_id, auto_open=False)

        js = js.format(url=url, container_id=self.container_id)

        self.plot_js = js

    def watcher(self):
        clear_output()
        image_shown = False
        plot_shown = False

        time.sleep(0.3)
        display(HTML(self.container_html()))

        while True:
            if not image_shown and self.png:
                self.image_code()
                display(Javascript(self.image_js))
                image_shown = True
            if not plot_shown and self.plot_js:
                display(Javascript(self.plot_js))
                plot_shown = True
            if plot_shown and (image_shown or self.image_failed):
                break
            time.sleep(0.05)

    def go(self, figure_or_data):
        plot_thread = threading.Thread(target=self.iframe_code, args=(figure_or_data, ))
        image_thread = threading.Thread(target=self.gen_image, args=(figure_or_data, ))
        watcher_thread = threading.Thread(target=self.watcher)

        plot_thread.start()
        image_thread.start()
        watcher_thread.start()
