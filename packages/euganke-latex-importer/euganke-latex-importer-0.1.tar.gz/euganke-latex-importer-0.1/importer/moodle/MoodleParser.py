# -*- coding: utf-8 -*-
__author__ = 'Miha'

from xml.dom.minidom import parse, Document, Node, NodeList, parseString
import json
import re


class MoodleParser:
    """
    This class converts Moodle xml into Euganke JSON
    """

    # ATTRIBUTES
    document = Document
    root = Node
    top_nodes = NodeList
    filtered_count = 0
    exercise_count = 0
    currentCategory = []

    def __init__(self, xml_file_path=None, xml_string=None):
        """
        NOTE: xml_string is used if both parameters are spceifyed.
        """
        if (not xml_file_path) and (not xml_string):
            raise Exception("Must specify xml_file_path or xml_string!")

        if xml_string:
            # read xml from string
            self.myxml = parseString(xml_string)
        else:
            # Read XML from file
            self.myxml = parse(xml_file_path)

        self.root = self.myxml.documentElement
        self.top_nodes = self.root.childNodes
        # NORMALIZIRAM
        self.root.normalize()

    def getJson_str(self):
        return json.dumps(self.getJson_obj())

    def getJson_obj(self):
        """
        Generates JSON object from xml
        """
        arrayVseh = []
        for curr in self.top_nodes:
            # NI PRAVI NODE
            if not self.isRealNode(curr):
                continue
            # JE DUMMY QUESTION
            if self.isDummyQuestionNode(curr):
                text = self.getChildNodeT(self.getChildNodeT(curr, "category"), "text")
                self.currentCategory = text.childNodes.item(0).nodeValue.split("/")
                continue
            # JE PRAVI QUESTION
            if self.isRealQuestionNode(curr):
                json_oblika_vprasanja = self.questionNodeToJSON(curr)
                if json_oblika_vprasanja:
                    arrayVseh.append(json_oblika_vprasanja)

        # na koncu
        self.exercise_count = len(arrayVseh)
        return arrayVseh

    def isRealNode(self, node):
        return node.nodeType == Node.ELEMENT_NODE

    def isDummyQuestionNode(self, realNode):
        if realNode.nodeName == "question" and realNode.getAttribute("type") == "category":
            return True
        return False

    def getChildNodeT(self, parent, tag):
        return parent.getElementsByTagName(tag).item(0)

    def isRealQuestionNode(self, realNode):
        if realNode.nodeName == "question" and realNode.getAttribute("type") != "category":
            return True
        return False

    def questionNodeToJSON(self, questionNode):
        exercise = {}
        # NASLOV NALOGE
        text = self.getChildNodeT(self.getChildNodeT(questionNode, "name"), "text")
        exercise["title"] = text.childNodes.item(0).nodeValue
        # TAGI
        exercise["tags"] = self.currentCategory
        # FILTRIRANJE NALOG PO BESEDILU
        if self.isBrokenExercise(self.readQuestionText(self.getChildNodeT(questionNode, "questiontext"))):
            self.filtered_count += 1
            return None

        # QUESTIONS
        question_type = questionNode.getAttribute("type")
        questions = []
        if question_type == "multichoice":
            questions = self.handleMultichoice(questionNode)
        elif question_type == "truefalse":
            questions = None
        elif question_type == "shortanswer":
            questions =self.handleShortAnswer(questionNode)
        elif question_type == "matching":
            questions = self.handleMatching(questionNode)
        elif question_type == "cloze":
            questions = None
        elif question_type == "essay":
            questions = None
        elif question_type == "numerical":
            questions = self.handleNumerical(questionNode)
        elif question_type == "description":
            questions = None

        if not questions:
            return None
        exercise["questions"] = questions

        exercise["meta"] = {
            "source": u"Spletna učilnica FRI",
            "id": str(
                hash(
                    "".join(exercise["tags"]).encode('utf-8') +
                    exercise["title"].encode('utf-8') +
                    question_type.encode('utf-8')
                )
            )
        }
        return exercise

    def handleMultichoice(self, questionNode):
        questions = []
        question = {}
        # TYPE
        question["type"] = "multichoice"
        # DATA
        data_q = {
            "type": "text/html",
            "text": self.readQuestionText(self.getChildNodeT(questionNode, "questiontext"))
        }
        question["data"] = data_q
        # META
        meta_q = {}
        # poglej ce je single
        isSingle = self.calculateIfIsSingleMultichoice(questionNode)
        input_type = "checkbox"
        if isSingle:
            input_type = "radio"
        meta_q["type"] = input_type
        question["meta"] = meta_q
        # ANSWER
        answer_array = []
        answers = self.getChildNodesT(questionNode, "answer")
        for answer in answers:
            ANSWER = {}
            answer_text = self.getChildNodeT(answer, "text")
            an_option = answer_text.childNodes.item(0).nodeValue
            # "data"
            data_a = {
                "type": "text/html",
                "text": an_option
            }
            ANSWER["data"] = data_a
            # "meta"
            meta_a = {}
            # pogledam ali je odgovor pravilen
            fraction = float(answer.getAttribute("fraction"))
            meta_a["match"] = fraction > 0
            ANSWER["meta"] = meta_a
            answer_array.append(ANSWER)
        question["answer"] = answer_array
        questions.append(question)
        return questions

    def readQuestionText(self, questionText):
        s = self.getChildNodeT(questionText, "text").childNodes.item(0).nodeValue
        return s

    def calculateIfIsSingleMultichoice(self, questionNode):
        single = self.getChildNodeT(questionNode, "single")
        single_val = single.childNodes.item(0).nodeValue
        if single_val == "true":
            return True
        return False

    def getChildNodesT(self, parent, tag):
        return parent.getElementsByTagName(tag)

    def handleShortAnswer(self, questionNode):
        questions = []
        question = {}
        # TYPE
        question["type"] = "shortanswer"
        # DATA
        data_q = {
            "type": "text/html",
            "text": self.readQuestionText(self.getChildNodeT(questionNode, "questiontext"))
        }
        question["data"] = data_q
        # ANSWER
        answer_array = []
        correct_answers = self.calculateAllCorrectAnswersShortanswer(questionNode)
        for correct_answer in correct_answers:
            answer = {}
            data_a = {
                "type": "text/plain",
                "text": correct_answer
            }
            answer["data"] = data_a
            answer_array.append(answer)
        question["answer"] = answer_array
        # POSEBEN PRIMER: SHORTANSWER JE V RESNICI NUMERICAL
        if len(correct_answers) == 1:
            flag = False
            numerical_value = 0
            try:
                numerical_value = float(correct_answers[0])  # trying to convert
                flag = True
            except Exception, e:
                flag = False
            if flag:
                self.convertShortanswerToNumerical(question, numerical_value)
        questions.append(question)
        return questions

    def calculateAllCorrectAnswersShortanswer(self, questionNode):
        ret = []
        answers = self.getChildNodesT(questionNode, "answer")
        for answer in answers:
            answer_text = self.getChildNodeT(answer, "text")
            answer_text_val = answer_text.childNodes.item(0).nodeValue
            ret.append(answer_text_val)
        return ret

    def convertShortanswerToNumerical(self, question, correct_answer):
        # popravim tipe
        question["type"] = "numerical"
        # popravim answer
        answer_array = question["answer"]
        firstAnswer = answer_array[0]
        # "data"
        data_a = firstAnswer["data"]
        data_a["type"] = "double"
        data_a["text"] = correct_answer
        # "meta"
        meta_a = {
            "precision": 0.01 # DEFAULT PRECISION
        }
        firstAnswer["meta"] = meta_a

    def handleMatching(self, questionNode):
        subquestions = self.getChildNodesT(questionNode, "subquestion")
        questions = []
        allOptions = self.calculateAllOptionsMatching(subquestions)
        question = {}
        # TYPE
        question["type"] = "matching"
        # DATA
        data_q = {
            "type": "text/html",
            "text": self.readQuestionText(self.getChildNodeT(questionNode, "questiontext"))
        }
        question["data"] = data_q
        # ANSWER - LEVE STRANI
        answer_array = []
        # ZA VSAK SUBQUESTION (moodle) NAREDIM SVOJ ANSWER (euganke)
        for subq in subquestions:
            answer = {}
            # "data"
            data_a = {
                "type": "text/html"
            }
            text = self.getChildNodeT(subq, "text")
            answer_text = self.getChildNodeT(self.getChildNodeT(subq, "answer"), "text")
            besedilo_levo = text.childNodes.item(0).nodeValue
            pravilniIzbor_desno = answer_text.childNodes.item(0).nodeValue
            data_a["text"] = besedilo_levo
            answer["data"] = data_a
            # "meta"
            meta_a = {
                "match": self.calculateMatchIdMatching(pravilniIzbor_desno, allOptions)
            }
            answer["meta"] = meta_a
            # dodam v array
            answer_array.append(answer)
        # ANSWER - DESNE STRANI
        for i in range(0, len(allOptions)):
            answer = {}
            # "data"
            data_a1 = {
                "type": "text/html",
                "text": allOptions[i]
            }
            answer["data"] = data_a1
            # "meta"
            meta_a1 = {
                "id": i
            }
            answer["meta"] = meta_a1
            # dodam v array
            answer_array.append(answer)
        question["answer"] = answer_array
        questions.append(question)
        return questions




    def calculateAllOptionsMatching(self, subquestions):
        ret = []
        allOptions = set()
        for subq in subquestions:
            answer_text = self.getChildNodeT(self.getChildNodeT(subq, "answer"), "text")
            allOptions.add(answer_text.childNodes.item(0).nodeValue)
        # prepisem v seznam
        for curr in allOptions:
            ret.append(curr)
        return ret

    def calculateMatchIdMatching(self, pravilniIzbor_desno, allOptions):
        for i in range(0, len(allOptions)):
            if allOptions[i] == pravilniIzbor_desno:
                return i
        print "MoodleParser.calculateMatchIdMatching()... NAPAKA - ne najdem ujemanja"
        return -1

    def handleNumerical(self, questionNode):
        questions = []
        question = {}
        # TYPE
        question["type"] = "numerical"
        # DATA
        data_q = {
            "type": "text/html",
            "text": self.readQuestionText(self.getChildNodeT(questionNode, "questiontext"))
        }
        question["data"] = data_q
        # ANSWER
        answer_text = self.getChildNodeT(self.getChildNodeT(questionNode, "answer"), "text")
        answer_tolerance = self.getChildNodeT(self.getChildNodeT(questionNode, "answer"), "tolerance")
        tocna_vrednost = float(answer_text.childNodes.item(0).nodeValue)
        dovoljeno_odstopanje = 0
        try:
            dovoljeno_odstopanje = float(answer_tolerance.childNodes.item(0).nodeValue)
        except Exception, e:
            dovoljeno_odstopanje = 0
        answer = {}
        data_a = {
            "type": "double",
            "text": tocna_vrednost
        }
        answer["data"] = data_a
        meta_a = {
            "precision": dovoljeno_odstopanje
        }
        answer["meta"] = meta_a
        answer_array = []
        answer_array.append(answer)
        question["answer"] = answer_array

        questions.append(question)
        return questions

    def isBrokenExercise(self, questiontext):
        # 1
        regex = r".+[?!:.$]+.*"
        if re.match(regex, questiontext):
            return False
        # 2
        regex = r".+ je.*"
        if re.match(regex, questiontext):
            return False
        # 3
        if len(questiontext) > 150:
            return False
        elif len(questiontext) > 40:
            regex = r"^[A-Z].*"
            if re.match(regex, questiontext):
                return False
        return True

class SpecialCommentsParser:
    """
    Class for parsing A. Jurisic's special file with comments.
    """

    def __init__(self, comments_file_path):
        self.comments_file = open(comments_file_path, "r")

    def generateDict(self):
        """
        Generates self.opombe and self.sifrant
        """
        STATE = "opombe"  # opombe, sifrant_vsebine
        SUBSTATE = "wait_next" # next_line, wait_next
        INDEX = -1
        self.opombe = {}
        self.sifrant = {}
        for line in iter(self.comments_file):
            # NORMALIZE LINE
            # strip whitespaces from both edges
            line = line.strip()
            # remove duplicate whitespaces from content
            line = re.sub(r"( )+", " ", line)

            # print "line: %s" % line

            if STATE == "opombe":
                if SUBSTATE == "wait_next":
                    try:
                        # FIND IDEX
                        parts = line.split(".")
                        new_index = int(parts[0])
                        new_ind_len = len(parts[0]) + 2  # pika in presledek
                        ################
                        if new_index > INDEX:
                            INDEX = new_index
                        else:
                            # low index indicates that we are parsing snov dict
                            # pase first line immediately, then change state
                            self.sifrant[new_index] = parts[1].strip()
                            STATE = "sifrant_vsebine"
                            continue
                        ################

                        line = line[new_ind_len:]

                        # FIND SNOV
                        snov = self.parseHalf("snov", line)
                        # split by commas
                        snov_numbers = []
                        parts = snov.split(",")
                        for p in parts:
                            try:
                                snov_numbers.append(int(p))
                            except:
                                pass

                        parts = line.split(r" \snov{")
                        if len(parts) < 2:
                            # seems there is no title present
                            line = ""
                        else:
                            line = parts[0]

                        # FIND TITLE
                        title = line

                        # BUILD DICT FOR THIS INDEX
                        self.opombe[INDEX] = {
                            "snov": snov_numbers,
                            "title": title
                        }

                        SUBSTATE = "next_line"
                        self.sticky_line = ""
                    except:
                        #print "not yet"
                        pass
                elif SUBSTATE == "next_line":
                    # empty line means end of this index
                    if line == "":
                        vsebina = self.parseOne("opombe", self.sticky_line)
                        vsebina = vsebina.strip()
                        self.opombe[INDEX]["vsebina"] = vsebina

                        SUBSTATE = "wait_next"
                        continue

                    # paste all oombe lines together
                    self.sticky_line += line
            if STATE == "sifrant_vsebine":
                # check for end of sifrant_vsebine
                if line == "":
                    print "End of document."
                    break

                parts = line.split(".")
                try:
                    num = int(parts[0])
                    self.sifrant[num] = parts[1].strip()
                except:
                    print "Problem parsing sifrant_vsebine"
                    pass

        import pdb; pdb.set_trace()
        return self.opombe

    def applyOpombe(self, exercise_array):
        """
        Adds opombe to exerciseses. Returns the edited array.
        """
        index = 0
        for exercise in exercise_array:
            print exercise["title"]
            if self.opombe.has_key(index):
                print "...Nasel sem opombe za %d (%s)" % (index, self.opombe[index]["title"])
                print "...dodano"

                # apply opombe
                exercise["meta"].update({
                    "opombe": self.opombe[index]["vsebina"]
                })

                # apply snov
                print "snov_numbers = ", self.opombe[index]["snov"]
                for snov_num in self.opombe[index]["snov"]:
                    if not self.sifrant.has_key(snov_num):
                        print "Opomba %d has invalid key for sifrant_snovi: %d. Skipping." % (index, snov_num)
                        index += 1
                        continue

                    if self.sifrant[snov_num] not in exercise["tags"]:
                        exercise["tags"].append({"value": self.sifrant[snov_num]})

            # transform tags into correct value
            for tag in exercise["tags"]:
                if not type(tag)==dict:
                    exercise["tags"].remove(tag)
                    exercise["tags"].append({"value":tag})
            index += 1


        return exercise_array

    def MERGE_obj(self, exercise_array):
        """
        Parse opombe and apply them on exercises.
        Returns array of merged exercises.
        """
        self.generateDict()
        return self.applyOpombe(exercise_array)

    def MERGE_str(self, exercise_array):
        """
        Parse opombe and apply them on exercises.
        Returns json string.
        """
        return json.dumps(self.MERGE_obj(exercise_array))

    def parseHalf(self, key, latex_string):
        """
        Returns content of first \key{content} ... element.
        """
        regex = re.compile(r"\\" + key + "\{(.*?)\}", re.DOTALL)
        value = regex.search(latex_string)
        if not value:
            return "MISSING"

        return value.group(1)

    def parseOne(self, key, latex_string, needParam2=False):
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

    def prettyPrintDict(self, d):
        print json.dumps(d, sort_keys=True, indent=4)
