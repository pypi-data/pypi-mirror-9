__author__ = 'miha'

import re
import json


def l2h(latex_string):
    """
    Replace latex elements with html elements.
    """
    #latex_string = l2h_lessthan(latex_string)
    latex_string = l2h_comments(latex_string)
    latex_string = l2h_newline(latex_string)
    latex_string = l2h_zanimivost(latex_string)
    latex_string = l2h_code(latex_string)
    latex_string = l2h_enumerate(latex_string)
    latex_string = l2h_figure(latex_string)
    latex_string = l2h_em(latex_string)
    latex_string = l2h_bf(latex_string)
    latex_string = l2h_url(latex_string)
    latex_string = l2h_eur(latex_string)

    return latex_string
def l2h_lessthan(tex):
    """
    Change < with &lt; in equations.
    """
    tex = tex.replace("<","&lt;")
    return tex

def l2h_zanimivost(tex):
    """
    \\begin{zanimivost}... to <p><div class="curiosity>
    """
    tex = re.sub(r"\\begin\{zanimivost\}\{(.*?)\}",r"<p><div class=\"curiosity\" data-title=\"\1\">",tex)
    tex = tex.replace("\\end{zanimivost}","</div></p>")
    return tex

def l2h_code(tex):
    """
    \\begin{verbatim}\\end{verbatim to <pre></pre>
    """
    tex = tex.replace("\\begin{verbatim}",'<div class="horizontal-scrollable">\n<pre>')
    tex = tex.replace("\\end{verbatim}","</pre>\n</div>")
    return tex

def l2h_newline(latex_string):
    """
    handle newlines and paragraphs
    """
    latex_string = latex_string.replace("\\newline","<br></br>")
    #latex_string = re.sub(r'(?imu)^\s*\n',r"<p>\n</p>\n",latex_string)
    return latex_string

def l2h_comments(latex_string):
    """
    Remove everything after %
    """
    return re.sub(r"(?imu)([^\\])%.*$","\1",latex_string)

def l2h_url(latex_string):
    """
    Replace \url{http://euganke.si} with
    <a href="http://euganke.si">http://euganke.si</a>
    and \href{http://euganke.si}{Euganke} withe
    <a href="http://euganke.si">Euganke</a>
    """

    latex_string = re.sub(r"\\url\{(.*?)\}",r'<a href="\1">\1</a>',latex_string)
    return re.sub(r"\\href\{(.*?)\}\{(.*?)\}",r'<a href="\1">\2</a>',latex_string)


def l2h_enumerate(latex_string):
    """
    Replaces all \begin{enumerate} with html list
    """
    latex_string = re.sub(r"\\begin\{enumerate\}", r"<ul>", latex_string)
    latex_string = re.sub(r"\\end\{enumerate\}", r"</ul>", latex_string)
    latex_string = re.sub(r"\\item", r"<li>", latex_string)

    return  latex_string

def l2h_figure(latex_string):
    """
    Replaces all \slika{}{} with <img> and
    Removes all \begin{figure}
    """

    # remove all figure
    latex_string = re.sub(r"\\begin\{figure\}.*?\\end\{figure\}", "", latex_string)
    # correct all slika
    # latex_string = latex_string.replace(r"\begin{slika}", "<p><img alt=\"slika\" src=\"/images/")
    # latex_string = latex_string.replace(r"\end{slika}", "\"/></p>")
    latex_string = re.sub(r"\\slika\{(.*?)\}\{(.*?)\.(png|PNG|jpg|jpeg|JPG)\s*\}",
                          r'<img data-pid="\2"/>',
                          latex_string)
    return latex_string

def l2h_em(latex_string):
    """
    Replaces all \em with <i>
    """
    latex_string = re.sub(r"\\emph\{(.*?)\}", r"<em>\1</em>", latex_string, flags=re.DOTALL|re.M)
    latex_string = re.sub(r"\{\\em(.*?)\}", r"<em>\1</em>", latex_string, flags=re.DOTALL|re.M)

    return latex_string

def l2h_bf(latex_string):
    """
    Replaces all \bf with <b>
    """
    latex_string = re.sub(r"\textbf\{(.*?)\}", r"<b>\g<1></b>", latex_string, re.DOTALL)
    latex_string = re.sub(r"\{\\bf (.*?)\}", r"<b>\g<1></b>", latex_string, re.DOTALL)

    return latex_string

def l2h_eur(latex_string):
    return re.sub("\\eur", "$\\eur$", latex_string)

def slika_replacement(matchobj):
    orig_path = matchobj.group(1)
    res = '<p><img data-pid="'
    res += orig_path
    res += '" /></p>'
    return res

def convert_image(orig_path):
    """
    Read image from orig_src then rename it and copy to desired location.
    Returns path to new image.
    """
    # TODO: rename/move

    final_path = "/images/" + orig_path
    return final_path


def getSectionContent(section, stop_sections):
    """
    Returns beginning content in this section.
    """
    first = None
    for stop in stop_sections:
        curr = section.find(r"\begin{" + stop + "}")  # \begin{stopword}
        if curr >= 0 and (not first or first > curr):
            first = curr

        curr = section.find("\\" + stop + " ")  # \stopword
        if curr >= 0 and (not first or first > curr):
            first = curr

        curr = section.find("\\" + stop + "{")  # \stopword{...}
        if curr >= 0 and (not first or first > curr):
            first = curr

    if first:
        return section[0:first]
    else:
        return section


def parseOne(key, latex_string, needParam2=False):
    """
    Returns content of first \begin{key} ... \end{key} element.
    If needParam2 is set, returns tuple (param2, content). NOTE: \begin{key}{param2}
    """
    regex = re.compile(r"\\begin\{" + key + r"\}(\{(.*?)\}){0,1}(.*?)\\end\{" + key + r"\}", re.DOTALL)
    value = regex.search(latex_string)
    if needParam2:
        if not value:
            return ("MISSING","MISSING")
        # (param2, value)
        return value.group(2), value.group(3)
    else:
        if not value:
            return "MISSING"
        # just value
        return value.group(3)

def parseAll(key, latex_string, needParam2=False):
    """
    Returns array of contents of all \begin{key} ... \end{key} elements
    If needParam2 is set, returns array of all tuples (param2, content). NOTE: \begin{key}{param2}
    """
    regex = re.compile(r"\\begin\{" + key + r"\}(\{(.*?)\}){0,1}(.*?)\\end\{" + key + r"\}", re.DOTALL)
    value = regex.findall(latex_string)
    # only take first and third group = (param2, value)
    v = []
    for tpl in value:
        if needParam2:
            if not value:
                return ("MISSING","MISSING")
            # (param2, value)
            v.append((tpl[1], tpl[2]))
        else:
            if not value:
                return "MISSING"
            # just value
            v.append(tpl[2])
    return v

def prettyPrintDict(d):
    print json.dumps(d, sort_keys=True, indent=4)

def parseHalf(key, latex_string):
    """
    Returns content of first \key{content} ... element.
    """
    regex = re.compile(r"\\" + key + "\{(.*?)\}", re.DOTALL)
    value = regex.search(latex_string)
    if not value:
        return "MISSING"

    return value.group(1)
