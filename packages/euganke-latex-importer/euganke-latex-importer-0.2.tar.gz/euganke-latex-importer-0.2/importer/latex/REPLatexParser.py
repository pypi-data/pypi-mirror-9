from PresekLatexParser import PresekLatexParser


class REPLatexParser(PresekLatexParser):
    def handleMeta(self, el):
        meta = super(REPLatexParser, self).handleMeta(el)
        try:
            id = next((v for k, v in meta.iteritems() if k == "id"))
        except:
            print "Exercise id not set !!!!!"
            return meta
        meta.update()
        meta.update({"_tekmovanje": id.split("-")[0]})
        meta.update({"_razred": id.split("-")[1]})
        meta.update({"_naloga": id.split("-")[2]})

        return meta
