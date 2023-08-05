__author__ = 'Miha'
import re
import json
from Common import *

class PresekLatexParser(object):
    exercise_keys_noParam = ["id", "vir", "letnik", "stran", "podrocje", "podpodrocje",
                              "naslov", "avtor", "besedilo","tags"]

    def __init__(self, whole_latex_string):
	# before we do anything, replace < with &lt;
	whole_latex_string = l2h_lessthan(whole_latex_string)
        # insert "naloga" sections if necessery
        whole_latex_string = whole_latex_string.replace(r"%=============================", r"\begin{naloga}")
        whole_latex_string = whole_latex_string.replace(r"\newpage", r"\end{naloga}")

        # use only part between \begin{document} \end{document}
        whole_latex_string = ''.join(parseAll("document", whole_latex_string))

        # Replace scriptsize and footsize with only what is betwene
        whole_latex_string = re.sub(
            r"\{\\(scriptsize|footnotesize)\s*\n?\s*\$\$(.*?)\$\$\s*\n?\s*\}",
            r'\2',
            whole_latex_string, flags=re.M|re.DOTALL
        )

        # Replace scriptsize and footsize with only what is betwene
        whole_latex_string = re.sub(
            r"\{\\scriptsize(.*?)\}\s*\%", r'\1',
            whole_latex_string, flags=re.M|re.DOTALL
        )

        whole_latex_string = re.sub(
            r"\\begin\{siroko\}(.*?)\\end\{siroko\}",
            r'<div class="horizontal-scrollable">\1</div>',
            whole_latex_string, flags=re.M|re.DOTALL
        )


        # Remove vskip
        whole_latex_string = re.sub(r"\\vskip(.*?)m", "", whole_latex_string)

        # Remove noindent
        whole_latex_string = re.sub(r"\\newline", "<br>", whole_latex_string)

	# Remove noindent
        whole_latex_string = re.sub(r"\\noindent", "", whole_latex_string)

        # Insert newlines
        whole_latex_string = re.sub(r"\\medskip", "<p></p>", whole_latex_string)

        # We remove comments by first peplacing all procents with placeholder
        # then removing comments, and at last replacing placeholder back
        # if you know a better and simpler method please replace!
        whole_latex_string = re.sub(r"\\%", "RPL_214234", whole_latex_string)
        whole_latex_string = re.sub(r"\%(.*)", "", whole_latex_string)
        whole_latex_string = re.sub(r"RPL_214234", "\\%", whole_latex_string)

        # correct em tags
        whole_latex_string = l2h_em(whole_latex_string)

        # correct picture tags
        whole_latex_string = l2h(whole_latex_string)

        # extract all exercises
        self.all_exercises = []
        for naloga in parseAll("naloga", whole_latex_string):
            exercise = {}
            for key in self.exercise_keys_noParam:
                exercise[key] = parseOne(key, naloga)
            exercise["vprasanja"] = parseAll("vprasanje", naloga, needParam2=True)
            exercise["slike"] = re.findall(r"data-pid=\"(.*?)\"", naloga)
            self.all_exercises.append(exercise)
        self.detected_count = len(self.all_exercises)

    def getJson_str(self):
        return json.dumps(self.getJson_obj())

    def getJson_obj(self):
        exercise_counter = 1
        exercise_array = []
        for el in self.all_exercises:
            #try:
                exercise = {}
                # NASLOV NALOGE
                exercise["title"] = el["naslov"] or "Naloga " + el["id"]
                # TAGI
                exercise["tags"] = self.handleTags(el)
                # Slike
                if len(el["slike"]) > 0:
                    exercise["resources"]=[{"resourceid": sl} for sl in el["slike"]]
                # META
                exercise["meta"] = self.handleMeta(el)
                # BESEDILO
                data_b = {
                    "type": "text/html",
                    "text": el["besedilo"].strip() if not el["besedilo"] == "MISSING" else ""
                }
                if data_b["text"]:
                    exercise["data"] = data_b
                # QUESTIONS
                questions_counter = 1
                questions = []
                for questiontype, q in el["vprasanja"]:
                    #print "%2d.%2d Detected question of type: %s." % (exercise_counter, questions_counter, questiontype)
                    q = q.strip()
                    if questiontype == "numerical":
                        questions.append(self.handleNumerical(q))
                    elif questiontype == "essay":
                        questions.append(self.handleEssay(q))
                    elif questiontype == "description":
                        questions.append(self.handleDescription(q))
                    elif questiontype == "multichoice":
                        questions.append(self.handleMultichoice(q))
                    else:
                        print exercise_counter, ": Unsupported yet!"
                    exercise_counter += 1
                    questions_counter += 1
                if not questions:
                    continue
                exercise["questions"] = questions
                exercise_array.append(exercise)
            #except Exception , e:
            #    print "Neveljavna naloga: "
            #    prettyPrintDict(el)
        self.parsed_count = len(exercise_array)
        return exercise_array

    def handleTags(self, el):
        return [{"value": tag.strip()} for tag in el["tags"].split(',') if tag]

    def handleDescription(self, vprasanje):
        question = {}
        # TYPE
        question["type"] = "description"
        # DATA
        data_q = {
            "type": "text/html",
            "text": vprasanje.strip()
        }
        if data_q["text"]:
            question["data"] = data_q
        return question

    def handleMeta(self, el):
        meta= {}
        new_key = ""
        for key in ["id","vir","avtor","letnik","stran"]:
            if el[key] != "MISSING" and el[key]:
		meta.update({(new_key or key): el[key]})

        return meta

    def handleEssay(self, vprasanje):
        question = {}
        # TYPE
        question["type"] = "essay"
        # DATA
        data_q = {
            "type": "text/html",
            "text": getSectionContent(vprasanje, ["odgovor", "namig", "rezultat"]).strip()
        }
        if data_q["text"]:
            question["data"] = data_q
        # EXPLANATION
        # try to handle both - if explanation is in "odgovor" or in "rezultat"
        txt = parseOne("odgovor", vprasanje)
        if txt == "MISSING":
            txt = parseOne("rezultat", vprasanje)
        data_e = {
            "type": "text/html",
            "text": txt.strip() if not txt == "MISSING" else ""
        }
        if data_e["text"]:
            question["explanation"] = {"data": data_e}
        # HINT
        hints_array = []
        hints = parseAll("namig", vprasanje)
        for h in hints:
            data_h = {
                "type": "text/html",
                "text": h.strip()
            }
            hint = {
                "meta": None,
                "data": data_h if data_h["text"] else None
            }
            hints_array.append(hint)
        question["hints"] = hints_array

        return question


    def handleMultichoice(self, vprasanje):
        question = {}
        # TYPE
        question["type"] = "multichoice"
        # DATA
        data_q = {
            "type": "text/html",
            "text": getSectionContent(vprasanje, ["odgovor", "namig", "rezultat"])
        }
        if data_q["text"]:
            question["data"] = data_q
        if "{odgovor" in data_q["text"]:
            question["data"] = {"type": "text/html", "text": None}
        # META
        meta_q = {}
        # poglej ce je single
        isSingle = self.calculateIfIsSingleMultichoice(vprasanje)
        input_type = "checkbox"
        if isSingle:
            input_type = "radio"
        meta_q["type"] = input_type
        question["meta"] = meta_q
        # ANSWER
        answer_array = []
        for fraction, an_option in parseAll("odgovor", vprasanje, needParam2=True):
            ANSWER = {}
            # "data"
            data_a = {
                "type": "text/html",
                "text": an_option
            }
            if data_a["text"]:
                ANSWER["data"] = data_a
            # "meta"
            meta_a = {}
            # pogledam ali je odgovor pravilen
            meta_a["match"] = fraction == "T"
            ANSWER["meta"] = meta_a
            answer_array.append(ANSWER)
        question["answer"] = answer_array
        # HINT
        hints_array = []
        hints = parseAll("namig", vprasanje)
        for h in hints:
            data_h = {
                "type": "text/html",
                "text": h.strip()
            }
            hint = {
                "meta": None,
                "data": data_h if data_h["text"] else None
            }
            hints_array.append(hint)
        question["hints"] = hints_array

        return question

    def calculateIfIsSingleMultichoice(self, vprasanje):
        correct_count = 0
        for fraction, answer in parseAll("odgovor", vprasanje, needParam2=True):
            if fraction == "T":
                correct_count += 1

        return correct_count == 1


    def handleNumerical(self, vprasanje):
        question = {}
        # TYPE
        question["type"] = "numerical"
        # DATA
        data_q = {
            "type": "text/html",
            "text": getSectionContent(vprasanje, ["odgovor", "rezultat", "namig"])
        }
        if data_q["text"]:
            question["data"] = data_q
        # ANSWER
        rez_all = parseAll("rezultat", vprasanje, needParam2=True)
        try:
            rez = rez_all[0]
            try:
                dovoljeno_odstopanje = float(rez[0].replace(",", "."))  # decimal dot
            except:
                dovoljeno_odstopanje = 0.01 # default
            # detect type
            if rez[0].strip()=="1/1":
                a_type = "fraction"
                tocna_vrednost = rez[1].strip()
            elif dovoljeno_odstopanje >= 1 or rez[0].strip()=='':
                try:
                    a_type = "integer"
                    tocna_vrednost = int(rez[1])
                except:
                    a_type = "double"
                    tocna_vrednost = float(rez[1].replace(",", "."))
            else:
                a_type = "double"
                tocna_vrednost = float(rez[1].replace(",", "."))
            answer = {}
            data_a = {
                "type": a_type,
                "text": tocna_vrednost
            }
            if data_a["text"]:
                answer["data"] = data_a
            meta_a = {
                "precision": dovoljeno_odstopanje,
                #"labels": []  # TODO
            }
            answer["meta"] = meta_a
            answer_array = []
            answer_array.append(answer)
            question["answer"] = answer_array
        except:
            question["type"] = "essay"
            #print "INFO: Numerical type without numerical result! Converted to essay type: %s" % vprasanje.replace('\n', "")

        # HINT
        hints_array = []
        hints = parseAll("namig", vprasanje)
        for h in hints:
            data_h = {
                "type": "text/html",
                "text": h.strip()
            }
            hint = {
                "meta": None,
                "data": data_h if data_h["text"] else None
            }
            hints_array.append(hint)
        question["hints"] = hints_array

        # EXPLANATION
        data_e = {
            "type": "text/html",
            "text": parseOne("odgovor", vprasanje).strip()
        }
        if data_e["text"]:
            question["explanation"] = {"data": data_e}
        return question

    def handleVector(self, vprasanje):
        question = {}
        # TYPE
        question["type"] = "numerical"
        # DATA
        data_q = {
            "type": "text/html",
            "text": getSectionContent(vprasanje, ["odgovor", "rezultat", "namig"])
        }
        if data_q["text"]:
            question["data"] = data_q
        # ANSWER
        rez_all = parseAll("rezultat", vprasanje, needParam2=True)
        try:
            dovoljeno_odstopanje = None
            tocne_vrednosti = []
            for rez in rez_all:
                if not dovoljeno_odstopanje:
                    try:
                        dovoljeno_odstopanje = float(rez[0].replace(",", "."))  # decimal dot
                    except:
                        dovoljeno_odstopanje = 0.01  # default
                tocna_vrednost = float(rez[1].replace(",", "."))
                tocne_vrednosti.append(tocna_vrednost)
            answer = {}
            data_a = {
                "type": "double",
                "text": tocne_vrednosti
            }
            if data_a["text"]:
                answer["data"] = data_a
            meta_a = {
                "precision": dovoljeno_odstopanje,
                "ordered": False,  # TODO
                "labels": []  # TODO
            }
            answer["meta"] = meta_a
            answer_array = []
            answer_array.append(answer)
            question["answer"] = answer_array
        except:
            question["type"] = "essay"
            # print "INFO: Numerical type without numerical result! Converted to essay type: %s" % vprasanje.replace('\n', "")

        # HINT
        hints_array = []
        hints = parseAll("namig", vprasanje)
        for h in hints:
            data_h = {
                "type": "text/html",
                "text": h.strip()
            }
            hint = {
                "meta": None,
                "data": data_h if data_h["text"] else None
            }
            hints_array.append(hint)
        question["hints"] = hints_array

        # EXPLANATION
        data_e = {
            "type": "text/html",
            "text": parseOne("odgovor", vprasanje).strip()
        }
        if data_e["text"]:
            question["explanation"] = {"data": data_e}
        return question
