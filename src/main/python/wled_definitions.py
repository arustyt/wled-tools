import re
import yaml

from decision_maker import DecisionMaker, DECISION_UPDATE, DECISION_REPLACE
from wled_constants import NAME_TAG, ID_TAG, DESCRIPTION_TAG, ALIASES_TAG


class WledDefinitions:

    def __init__(self, definitions_file: str, definition_list_tag: str, decision_maker: DecisionMaker):
        self.decision_maker = decision_maker
        self.definition_list_tag = definition_list_tag
        with open(definitions_file) as f:
            self.definition_data = yaml.safe_load(f)

        self.definitions_by_name = {}
        self.definitions_by_id = {}
        for definition in self.definition_data[self.definition_list_tag]:
            definition_name_normalized = self.normalize_definition_name(definition[NAME_TAG])
            definition_details = {NAME_TAG: definition[NAME_TAG], ID_TAG: definition[ID_TAG],
                                  DESCRIPTION_TAG: definition[DESCRIPTION_TAG]}

            if ALIASES_TAG in definition:
                definition_details[ALIASES_TAG] = set(definition[ALIASES_TAG])
                for alias in definition[ALIASES_TAG]:
                    alias_name_normalized = self.normalize_definition_name(alias)
                    self.definitions_by_name[alias_name_normalized] = definition_details

            self.definitions_by_name[definition_name_normalized] = definition_details
            self.definitions_by_id[definition[ID_TAG]] = definition_details

        self.modified = False

    def normalize_definition_name(self, definition_name):
        definition_name_normalized = str(definition_name).lower()
        definition_name_normalized = re.sub('[ _]', '', definition_name_normalized)
        return definition_name_normalized

    #  Returns dict containing definition data: name, id, desc and aliases (if any)
    def get_by_name(self, definition_string):
        definition = None
        definition_string_normalized = self.normalize_definition_name(definition_string)
        if definition_string_normalized in self.definitions_by_name:
            definition = self.definitions_by_name[definition_string_normalized]
        else:
            raise ValueError("Input '{name}' is not a recognized definition name".format(name=definition_string))

        return definition

    #  Returns dict containing definition data: name, id, desc and aliases (if any)
    def get_by_id(self, definition_id):
        definition = None
        if definition_id in self.definitions_by_id:
            definition = self.definitions_by_id[definition_id]
        else:
            raise ValueError("Input '{id}' is not a recognized definition id".format(id=definition_id))

        return definition

    def is_modified(self):
        return self.modified

    def merge(self, new_definitions):
        if isinstance(new_definitions, list):
            self.merge_list(new_definitions)
        else:
            raise ValueError("{type} data structure is not supported.".format(type=str(type(new_definitions))))

    def merge_list(self, new_definitions):
        i = 0
        for definition_name in new_definitions:
            self.merge_definition(i, definition_name)
            i += 1

    def merge_definition(self, definition_id, definition_name, definition_desc=None):
        try:
            definition = self.get_by_id(definition_id)
            self.update_definition(definition, definition_name, definition_desc)
        except ValueError:
            self.create_definition(definition_id, definition_name, definition_desc)

    def update_definition(self, definition, new_name, new_desc):
        if self.definition_changed(definition, new_name, new_desc):
            self.handle_definition_change(definition, new_name, new_desc)

    def handle_definition_change(self, definition, new_name, new_desc):
        new_definition = {NAME_TAG: new_name, DESCRIPTION_TAG: new_desc}
        decision = self.decision_maker.handle_change(definition, new_definition)
        if decision == DECISION_UPDATE:
            if new_name != definition[NAME_TAG]:
                if ALIASES_TAG in definition:
                    aliases = definition[ALIASES_TAG]
                    if new_name not in aliases:
                        aliases.add(new_name)
                        self.modified = True
                else:
                    definition[ALIASES_TAG] = {new_name}
                    self.modified = True

            if new_desc is not None:
                definition[DESCRIPTION_TAG] = new_desc
                self.modified = True
        elif decision == DECISION_REPLACE:
            definition[NAME_TAG] = new_name
            definition[DESCRIPTION_TAG] = new_desc
            definition[ALIASES_TAG] = None
        # else DECISION_SKIP

    def definition_changed(self, definition, new_name, new_desc):
        name_not_an_alias = ALIASES_TAG not in definition or new_name not in definition[ALIASES_TAG]
        name_is_new = new_name != definition[NAME_TAG] and name_not_an_alias
        current_desc = definition[DESCRIPTION_TAG] if DESCRIPTION_TAG in definition else None
        description_is_new = new_desc is not None and new_desc != current_desc

        return name_is_new or description_is_new

    def create_definition(self, definition_id, definition_name, definition_desc):
        definition_name_normalized = self.normalize_definition_name(definition_name)
        definition_details = {NAME_TAG: definition_name_normalized, ID_TAG: definition_id,
                              DESCRIPTION_TAG: definition_desc}

        self.definitions_by_name[definition_name_normalized] = definition_details
        self.definitions_by_id[definition_id] = definition_details
        self.modified = True

    def dump(self):
        definition_list = []
        for definition_id in self.definitions_by_id:
            definition = self.definitions_by_id[definition_id]
            out_definition = {ID_TAG: definition[ID_TAG], NAME_TAG: definition[NAME_TAG], DESCRIPTION_TAG: definition[DESCRIPTION_TAG]}
            if ALIASES_TAG in definition and definition[ALIASES_TAG] is not None:
                out_definition[ALIASES_TAG] = list(definition[ALIASES_TAG])
            definition_list.append(out_definition)
        return {self.definition_list_tag: definition_list}


