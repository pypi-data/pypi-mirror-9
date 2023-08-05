import os
import codecs
import argparse


def readMultipleFiles(filenames):
    s = []
    for filename in filenames:
        file = codecs.open(filename, encoding="utf8", mode="r")
        s += [file.read()]
        file.close()

    return s

def main():
    from restapi import RestApi

    parser = argparse.ArgumentParser(description='Import some exercises')
    parser.add_argument('files', nargs='+', help="files to import")
    parser.add_argument('--type', default=None,
                        help="type of importer (presek, fapp, moodle, bober, ...)")
    parser.add_argument('--replace', action="store_true",
                        help="should exercises be replaced (default: false)")
    parser.add_argument('--token', default=os.environ.get("TOKEN"),
                        help="your userid (default: USERID environment variable)")
    parser.add_argument('--group', default=os.environ.get("GROUP"),
                        help="group name where to import (default: GROUP environment variable)")
    parser.add_argument('--imagedir', default=os.environ.get("IMGDIR"),
                        help="location of images (default: IMGDIR environment variable)")
    parser.add_argument('--exercises', nargs='+',
                        help="list of exercise id's (import all if not set)")
    parser.add_argument(
        '--url',
        default=os.environ.get("EUGANKE_URL") or "http://euganke.fri.uni-lj.si/api",
        help="api url (default: EUGANKE_URL environment variable of http://euganke.fri.uni-lj.si/api)"
    )

    args = parser.parse_args()
    if not args.type == "bober":
        content = readMultipleFiles(args.files)

    if args.type == "presek":
        from latex.PresekLatexParser import PresekLatexParser
        lp = PresekLatexParser("".join(content))
        exercises = lp.getJson_obj()
    elif args.type == "fapp":
        from latex.FAPPLatexParser import FAPPLatexParser
        lp = FAPPLatexParser("".join(content))
        exercises = lp.getJson_obj()
    elif args.type == "rep":
        from latex.REPLatexParser import REPLatexParser
        lp = REPLatexParser("".join(content))
        exercises = lp.getJson_obj()
    elif args.type == "moodle":
        from moodle.MoodleParser import MoodleParser, SpecialCommentsParser
        #import pdb; pdb.set_trace()
        mp = MoodleParser(xml_string=open(args.files[0], "r").read())
        scp = SpecialCommentsParser(args.files[1])
        lp = mp.getJson_obj()
        exercises = scp.MERGE_obj(lp)
    elif args.type == "bober":
        from bober.BoberParser import BoberParser
        bp = BoberParser()
        exercises = bp.getJson_obj()

    rest = RestApi(
        args.url, args.token, args.group, args.imagedir, args.type
    )

    #print "Skupno je zaznanih %d nalog." % lp.detected_count
    #print "Pravilno je pretvorjenih %d nalog." % lp.parsed_count

    # upload to database
    for exercise in exercises:
        if args.exercises:
            if not any((k == "id" and v in args.exercises
                        for k, v in exercise["meta"].iteritems())):
                continue

        rest.update_exercise(exercise, args.replace)

if __name__ == '__main__':
    main()
