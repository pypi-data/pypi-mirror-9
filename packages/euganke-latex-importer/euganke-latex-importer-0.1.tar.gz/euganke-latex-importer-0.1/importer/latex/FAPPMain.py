__author__ = 'Miha'
from FAPPLatexParser import FAPPLatexParser

def readMultipleFiles(base_path, filenames):
    s = ""
    for filename in filenames:
        path = base_path + filename
        file = open(path, "r")
        s += file.read()
        file.close()
    return s



if __name__ == '__main__':
    # read latex xml file to local variable (string)
    # path = "Z:/repos/euganke_web_parsersapi/euganke/extensions/LATEX_FILES/euganke01.tex"
    # file = open(path, "r")
    # content = file.read()
    # file.close()
    filenames = ["n.tex"]
    # filenames = ["euganke01.tex", "euganke02.tex", "euganke03.tex", "euganke04.tex", "euganke05.tex", "euganke06.tex",
    #              "euganke07.tex"]
    content = readMultipleFiles("/home/miha/euganke_web_parsersapi/euganke/extensions/LATEX_FILES/", filenames)

    # instantiate latexParser with given tex string
    lp = FAPPLatexParser(content)
    json_str = lp.getJson_str()
    print "Skupno je zaznanih %d nalog." % lp.detected_count
    print "Pravilno je pretvorjenih %d nalog." % lp.parsed_count

    # WRITE TO FILE
    file = open("/home/miha/euganke_web_parsersapi/euganke/extensions/OUTPUT/n.txt", "w")
    file.write(json_str)
    file.flush()
    file.close()