from BoberParser import BoberParser

__author__ = 'Miha'

#
# example of usege of bober parser module
#

if __name__ == '__main__':
    # read postgres file to local variable (string)
    postgres_file = open("Z:/repos/euganke_web_parsersapi/euganke/extensions/BOBER_FILES/bober_psql_dump.sql", "r")
    psql_dump_strig = postgres_file.read()


    # instantiate boberParser with given postgres string
    bp = BoberParser(psql_dump_strig)
    json_str = bp.getJson_str()
    print json_str
    print "Stevilo nalog: ", bp.exercise_count


    # WRITE TO FILE
    file = open("Z:/repos/euganke_web_parsersapi/euganke/extensions/OUTPUT/bober2013.txt", "w")
    file.write(json_str)
    file.flush()
    file.close()



