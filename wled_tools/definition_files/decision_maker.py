
DECISION_UPDATE = 'u'
DECISION_REPLACE = 'r'
DECISION_SKIP = 's'
DECISION_CREATE = 'c'
DECISION_REPLACE_NAME = 'n'
DECISION_REPLACE_NAME_WITH_ALIAS = 'a'

DECISION_YES = 'y'
DECISION_NO = 'n'


decisions = {DECISION_UPDATE: DECISION_UPDATE,
             DECISION_REPLACE: DECISION_REPLACE,
             DECISION_CREATE: DECISION_CREATE,
             DECISION_SKIP: DECISION_SKIP,
             DECISION_REPLACE_NAME: DECISION_REPLACE_NAME,
             DECISION_REPLACE_NAME_WITH_ALIAS: DECISION_REPLACE_NAME_WITH_ALIAS}


class DecisionMaker:

    def handle_change(self, old_value, new_value):
        print("Current Value: {value}".format(value=str(old_value)))
        print("New Value:     {value}".format(value=str(new_value)))
        while True:
            user_input = input("[U]pdate, [R]eplace, replace [N]ame, or [S]kip [U|R|N|S]? ").lower()
            if user_input in decisions:
                decision = decisions[user_input]
                break
        if decision == DECISION_REPLACE_NAME:
            while True:
                user_input = input("Keep current name as alias [Y|N]? ").lower()
                if user_input == DECISION_YES:
                    decision = DECISION_REPLACE_NAME_WITH_ALIAS
                    break
                elif user_input == DECISION_NO:
                    break

        return decision

    def handle_new(self, new_value):
        print("New Value:     {value}".format(value=str(new_value)))
        while True:
            user_input = input("[C]reate or [S]kip [C|S]? ")
            if user_input in decisions:
                decision = decisions[user_input]
                break
        return decision
