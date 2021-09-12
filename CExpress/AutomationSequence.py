'''
Created on Mar 30, 2017

@author: nsinha
'''

import re
from collections import OrderedDict


class ProcessSequenceStep(object):
    '''
    classdocs
    '''

    __processname = None
    __sequenceSteps = []

    def __init__(self, processname):
        """
        Initiallizes the Process ProcessSequence Step with a processname
        """
        self.__processname = processname
        self.__sequenceSteps = {}

    def addProcessSequenceStep(self, step):
        """
        Adds ProcessSequence Step
        """
        self.__sequenceSteps.append(step)

    def getProcessSequenceSteps(self):
        """
        Returns the sequence Steps
        """
        return self.__sequenceSteps


class SequenceStep(object):
    '''
    classdocs
    '''

    __name = None
    __cmdObject = OrderedDict()

    parsedict = None

    def __init__(self, sequenceName=None):
        '''
        Constructor
        '''
        self.__name = sequenceName
        self.parsedict = {}

    def addParseExtract(self, varname, regexp):
        """
        Add a ParseExtract Object
        """
        self.parsedict[varname] = regexp

    def addSequenceStep(self, stepName, cmdObject):
        """
        Adds a command object with a stepName 
        """
        self.__cmdObject[stepName] = cmdObject

    def getSequenceStep(self, stepName):
        """
        Returns the ProcessSequence step object corresponding to stepname
        """

    def getSequenceSteps(self):
        """
        Returns the SequenceStep steps ordered dictionary
        """
        return self.__cmdObject


class ParseEngine(object):
    """
    Handle buffer parsing from pre-defined
    regular expressions
    """
    _regex_dict = {}
    _expect_dict = {}
    _callback_dict = {}

    def __init__(self, key=None, regex=None, expect=None, 
                 matchcallback=None, notmatchcallback=None):
        if key is not None:
            self._regex_dict[key] = regex
            if expect is not None:
                self._expect_dict[key] = expect
                print("Adding expect key, {}: {}".format(key, expect))
                if matchcallback is not None:
                    self._callback_dict["True"] = matchcallback
                if notmatchcallback is not None:
                    self._callback_dict["False"] = notmatchcallback

    def getparseextract(self):
        """
        Returns the dict of the parse extract defintions
        """
        return self._regex_dict

    def addparser(self, key, regex, expect=None, matchcallback=None, notmatchcallback=None):
        """
        Add regular expression to be stored
        and called upon during parsing activity.

        After defining regex, use extract for matching

        + key - name of regex
        - regex - regular expression
        """
        self._regex_dict[key] = re.compile(regex)
        if expect:
            self._expect_dict[key] = expect
            print("Adding expect key, {}: {}".format(key, expect))
        if matchcallback is not None:
            self._callback_dict["True"] = matchcallback
        if notmatchcallback is not None:
            self._callback_dict["False"] = notmatchcallback

    def get_expect_keys(self):
        """
        List of expected values corresponding to each key

        :return:
        """
        return self._expect_dict

    def extract(self, buffstring, keys=None):
        """
        Extract regex from buffer from predefined
        key using re.search()

        Returns dictionary in format of {key: matchtext}

        If regex included group(s), matchtext will be last
        group matched
        """
        returndict = {}

        for key in keys:
            returndict[key] = None

            if key not in self._regex_dict:
                continue

            regexresult = re.search(self._regex_dict[key], buffstring)

            if regexresult:
                # length of groups will indicate last item to group and return
                num_groups = len(regexresult.groups())
                returndict[key] = regexresult.group(num_groups)

        return returndict

    def getkeys(self):
        """
        Returns list of keys defined
        :return:
        """
        keys = self._regex_dict.keys()

        return keys


    def extractkeys(self, buffer):
        """
        Extract regex from buffer from predefined
        key using re.search()

        Returns dictionary in format of {key: matchtext}

        If regex included group(s), matchtext will be last
        group matched
        """
        returndict = {}

        for key in self._regex_dict.keys():
            regexresult = re.search(self._regex_dict[key], buffer)

            if regexresult:
                # length of groups will indicate last item to group and return
                num_groups = len(regexresult.groups())
                matchState = False
                if regexresult.group(num_groups) == self._expect_dict[key]:
                    matchState = True

                callbackkey = str(matchState)
                print("CallBackKey: %s" % (callbackkey))
                # contrsuct a dict
                keyobj = {}
                keyobj['value'] = str(regexresult.group(num_groups)).strip()
                keyobj['match'] = matchState

                if 'True' in self._callback_dict:
                    keyobj['callback'] = self._callback_dict['True']
                if 'False' in self._callback_dict:
                    keyobj['callback'] = self._callback_dict['False']
                returndict[key] = keyobj

        # print "Keys: %s" % (returndict)
        return returndict


# def test_parse_extract():
#     buffer = """
#         hi this is james and this
#         is my test_parse_extract module code.
#         version = 10.125.3:A2
#         we can create regex's and take action
#         based on the key value defined
#         by the user
#     """
#     parse = ParseExtract()
#
#     parse.addparser('james', 'hi.this.*(ja.es)')
#     parse.addparser('version', 'version.=.(.*)')
#     parse.addparser('module', 'module')
#
#     print parse.extract(buffer, 'james', 'version', 'module')
#
# test_parse_extract()


class CommandObject(object):
    """
    Command Object Definition
    """

    cmdstr = None
    timeout = None
    prompt = None
    buffer = None

    parseex = None

    def __init__(self, cmdstr, timeout, prompt):
        """
        Command Object 
        """
        self.cmdstr = "%s\r" % (cmdstr)
        self.timeout = timeout
        self.prompt = prompt

    def getCommand(self):
        """
        Get Command
        """
        cmdobj = {}
        cmdobj["cmd"] = self.cmdstr
        cmdobj["timeout"] = self.timeout
        cmdobj["prompt"] = self.prompt

        if self.parseex is not None:
            cmdobj["parseext"] = self.parseex
        return cmdobj

    def addParseExtract(self, parseex):
        """
        Adds parse extract object
        + parseex
        """
        self.parseex = parseex

    def getParseExtract(self):
        """
        """
        return self.parseex
