
DECISION_UPDATE = 'u'
DECISION_REPLACE = 'r'
DECISION_SKIP = 's'
DECISION_ADD = 'a'

decisions = {DECISION_UPDATE: DECISION_UPDATE,
             DECISION_REPLACE: DECISION_REPLACE,
             DECISION_ADD: DECISION_ADD,
             DECISION_SKIP: DECISION_SKIP}


class DecisionMaker:

    def handle_change(self, old_value, new_value):
        print("Current Value: {value}".format(value=str(old_value)))
        print("New Value:     {value}".format(value=str(new_value)))
        while True:
            user_input = input("Update, Replace, or Skip [U|R|S]?").lower()
            if user_input in decisions:
                decision = decisions[user_input]
                break
        return decision

    def handle_new(self, new_value):
        print("New Value:     {value}".format(value=str(new_value)))
        while True:
            user_input = input("Create or Skip [A|S]?")
            if user_input in decisions:
                decision = decisions[user_input]
                break
        return decision
