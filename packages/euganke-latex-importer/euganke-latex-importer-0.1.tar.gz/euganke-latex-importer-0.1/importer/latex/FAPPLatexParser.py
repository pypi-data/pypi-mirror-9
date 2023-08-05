__author__ = 'Miha'
import re
import json

from PresekLatexParser import PresekLatexParser


class FAPPLatexParser(PresekLatexParser):
    def __init__(self, whole_latex_string):
        groups = re.compile(r"\\\\begin\{tags\}(.*),/\\\\begin\{tags\}(.*) /")
        self.tag_mappings = {k: v for k, v in groups.findall(whole_latex_string)}

        super(FAPPLatexParser, self).__init__(whole_latex_string)

    #def handleTags(self, el):
        #id = el.get("tags", "").split(",")[0]
        #if id and self.tag_mappings.get(id):
            #return [{"value": self.tag_mappings.get(id).replace(",", "")}]

        #return []
