## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

class FakeInteract(object):
    """ A class to tests code depending on qisys.interact

    """
    def __init__(self):
        self.answers_type = None
        self.answer_index = -1
        self._answers = None
        self.questions = list()

    @property
    def answers(self):
        if self._answers is None:
            raise Exception("FakeInteract not initialized")
        return self._answers

    # pylint: disable-msg=E1101
    @answers.setter
    # pylint: disable-msg=E0102
    def answers(self, value):
        if type(value) == type(dict()):
            self.answers_type = "dict"
        elif type(value) == type(list()):
            self.answers_type = "list"
        else:
            raise Exception("Unknow answer type: " + type(value))
        self._answers = value

    def find_answer(self, message, choices=None, default=None):
        keys = self.answers.keys()
        for key in keys:
            if key in message.lower():
                if not choices:
                    return self.answers[key]
                answer = self.answers[key]
                if answer in choices:
                    return answer
                else:
                    mess  = "Would answer %s\n" % answer
                    mess += "But choices are: %s\n" % choices
                    raise Exception(mess)
        if default is not None:
            return default
        mess  = "Could not find answer for\n  :: %s\n" % message
        mess += "Known keys are: %s" % ", ".join(keys)
        raise Exception(mess)

    def ask_choice(self, choices, message, **unused):
        print "::", message
        for choice in choices:
            print "* ", choice
        answer = self._get_answer(message, choices)
        print ">", answer
        return answer

    def ask_yes_no(self, message, default=False):
        print "::", message,
        if default:
            print "(Y/n)"
        else:
            print "(y/N)"
        answer = self._get_answer(message, default=default)
        print ">", answer
        return answer

    def ask_path(self, message):
        print "::", message
        answer = self._get_answer(message)
        print ">", answer
        return answer

    def ask_string(self, message):
        print "::", message
        answer = self._get_answer(message)
        print ">", answer
        return answer

    def ask_program(self, message):
        print "::", message
        answer =  self._get_answer(message)
        print ">", answer
        return answer

    def _get_answer(self, message, choices=None, default=None):
        question = dict()
        question['message'] = message
        question['choices'] = choices
        question['default'] = default
        self.questions.append(question)
        if self.answers_type == "dict":
            return self.find_answer(message, choices=choices, default=default)
        else:
            self.answer_index += 1
            return self.answers[self.answer_index]
