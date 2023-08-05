from MoodleParser import MoodleParser

__author__ = 'Miha'

#
# example of usege of moodle parser module
#

if __name__ == '__main__':
    # read moodle xml file to local variable (string)
    moodle_file = open("Z:/repos/euganke_web_parsersapi/euganke/extensions/MOODLE_FILES/kategorijaOVS.xml", "r")
    moodle_xml_string = moodle_file.read()


    # instantiate moodleParser with given xml string
    mp = MoodleParser(xml_string=moodle_xml_string)
    json_str = mp.getJson_str()
    print json_str
    print "Stevilo nalog: ", mp.exercise_count
    print "Stevilo izlocenih nalog: ", mp.filtered_count

    # WRITE TO FILE
    file = open("Z:/repos/euganke_web_parsersapi/euganke/extensions/OUTPUT/kategorijaOVS.txt", "w")
    file.write(json_str)
    file.flush()
    file.close()