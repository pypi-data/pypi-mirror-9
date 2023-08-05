__author__ = 'Martin'

import re
import psycopg2
import json

class BoberParser:
    """
    Convert exercises from postgresql database to euganke.
    Suggested usage:
        bp = BoberParser(database_strig)
        json_obj = bp.getJson_obj()  # returns python dicts
        json_str = bp.getJson_str()  # returns string representation

    """
    sql = """
SELECT
    questions.id as id,
    questions.name as name,
	questions.question as question,
	questions."answerDescription" as explanation,
	    (SELECT array_agg(answer)
	    FROM answers
	    WHERE answers.question_id = questions.id)
    as answers,
	    (SELECT array_agg(score)
	    FROM answers
	    WHERE answers.question_id = questions.id)
    as score,
	    (SELECT questiontypes.description
	    FROM questiontypes
	    WHERE questiontypes.id = questions."questionTypeId")
    as type,
	    (SELECT questionlevels.description
	    FROM questionlevels
	    WHERE questionlevels.id = questions."questionLevelId")
    as level,
	    (SELECT categories.name
	    FROM categories
	    WHERE categories.id = questions.category_id)
    as category,
        (SELECT years.year
        FROM years,categories
        WHERE years.id=categories.year_id and categories.id = questions.category_id)
    as year
FROM
  public.questions
WHERE
  questions."isActive" = True
  """
    exercise_count = 0

    def __init__(self, database_string="dbname=bober"):
        self.exercises = []
        conn = psycopg2.connect(database_string)
        #import pdb; pdb.set_trace()
        cursor = conn.cursor()
        cursor.execute(self.sql)
        for line in cursor.fetchall():
            self.exercises.append(self.bober2euganke(line))
        self.exercise_count=len(self.exercises)

    def bober2euganke(self,line):
        keys = ["id","title","question","explanation","answers","score","type","level","category","year"]
        exercise = dict(zip(keys,line))
        # handle images in question and explanation
        for key in ["question","explanation"]:
            exercise[key] = self.handle_images(exercise[key])
        # handle images in answers as well
        for idx, answer in enumerate(exercise["answers"]):
            exercise["answers"][idx] = self.handle_images(answer)
        # META
        exercise["meta"]={"id": "bober%d" % exercise["id"]}
        for key in ["level","category","year"]:
            exercise["meta"].update({key: exercise[key]})
        # NASLOV NALOGE
        exercise["data"]={"text":exercise["question"],"type":"text/html"}
        # TAGI
        exercise["tags"] = [{"value": tag} for tag in exercise["type"].split(',')]
        # AVTOR
        exercise["author"] = {"name": "prof. dr. Andrej Brodnik, Niko Colneric", "institution": "ACM Slovenija, Tekmovanje Bober", "url": "http://tekmovanja.acm.si/bober"}
        # QUESTION
        questions = self.handleMultichoice(exercise)
        if questions:
            exercise["questions"] = questions
        # IMAGES
        exercise["slike"] = re.findall(r"data-pid=\"(.*?)\"",
            exercise["question"]+exercise["explanation"]+"".join(exercise["answers"]))
        if len(exercise["slike"]) > 0:
            exercise["resources"]=[{"resourceid": sl} for sl in exercise["slike"]]

        return exercise

    def handleMultichoice(self, exercise):
        question = {}
        # TYPE
        question["type"] = "multichoice"
        # Find last question
        quest  =  re.findall(r'(?s)<p>(.*?)</p>',exercise["question"])
        if len(quest)>0:
            text = quest[-1]
        else:
            text = u"Opcije:"
        data_q = {
            "type": "text/html",
            "text": text
        }
        question["data"] = data_q
        # META
        # poglej ce je single
        isSingle = sum(exercise["score"])<=1
        if isSingle:
            meta_q = {"type": "radio"}
        else:
            meta_q = {"type": "checkbox"}
        question["meta"] = meta_q
        # ANSWER
        answer_array = []
        # combine answers and scores
        answers  = zip(*[exercise["answers"],exercise["score"]])
        for answer in answers:
            an_option = self.cut_p(answer[0])
            # "data"
            data_a = {
                "type": "text/html",
                "text": an_option
            }
            # "meta"
            meta_a = {"match": answer[1]>0 }
            ANSWER = {"meta": meta_a, "data":data_a}
            answer_array.append(ANSWER)
        question["answer"] = answer_array
        if exercise["explanation"].strip():
            question["explanation"] = {"data":{"text":exercise["explanation"],"type":"text/html"}}
        return [question]

    def handle_images(self,text):
        """
        Change <img src=> tag to

        """
        return re.sub(r'(?is)<img(.*?)src=".*?([^/]*?)\.(gif|png|jpg)\"',
                r'<img \1 data-pid="\2"',text)
    def cut_p(self, s):
        forbidden_surrounding = ["<p>", "<div>"]
        for niz in forbidden_surrounding:
            l = len(niz)
            closing = "</" + niz[1:]
            if s[0:l] == niz and s[-(l+1):] == closing:
                s = s[l:-(l+1)]
                return s
        return s

    def getJson_obj(self):
        return self.exercises

    def getJson_str(self):
        # read the sqlite and create array of json exercises for euganke
        return json.dumps(self.exercises)



