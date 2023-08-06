import os
import shutil
import logging
from libs.read import load_data
from libs.report import make_profile
from libs.utils import safe_dirs
import templates

logger = logging.getLogger('report')


def report(args):
    """
    Create report in html format
    """
    logger.info("reading sequeces")
    data = load_data(args.json)
    out_dir = os.path.join(args.out, "html")
    safe_dirs(out_dir)

    logger.info("create profile")
    make_profile(data, out_dir, args)

    path_template = os.path.normpath(os.path.dirname(os.path.realpath(templates.__file__)))
    css_template = os.path.join(path_template, "info.css")
    js_template = os.path.join(path_template, "jquery.tablesorter.min.js")
    css = os.path.join(out_dir, "info.css")
    js = os.path.join(out_dir, "jquery.tablesorter.min.js")
    if not os.path.exists(css):
        shutil.copy(css_template, css)
        shutil.copy(js_template, js)
    logger.info("Done")
