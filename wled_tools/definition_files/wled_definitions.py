import re
from collections import OrderedDict

import yaml

from definition_files.decision_maker import DecisionMaker, DECISION_UPDATE, DECISION_REPLACE, DECISION_REPLACE_NAME, \
    DECISION_REPLACE_NAME_WITH_ALIAS, DECISION_CREATE, DECISION_DELETE
from wled_constants import NAME_TAG, ID_TAG, DESCRIPTION_TAG, ALIASES_TAG


class WledDefinitions:

    def __init__(self, definitions_file: str, definition_list_tag: str, decision_maker: DecisionMaker):
        self.decision_maker = decision_maker
        self.definition_list_tag = definition_list_tag
        with open(definitions_file) as f:
            self.definition_data = yaml.safe_load(f)

        self.definitions_by_name = {}
        self.definitions_by_id = OrderedDict()
        for definition in self.definition_data[self.definition_list_tag]:
            definition_name_normalized = self.normalize_name(definition[NAME_TAG])
            definition_details = OrderedDict()
            definition_details[ID_TAG] = definition[ID_TAG]
            definition_details[NAME_TAG] = definition[NAME_TAG]

            if DESCRIPTION_TAG in definition:
                definition_details[DESCRIPTION_TAG] = definition[DESCRIPTION_TAG]

            if ALIASES_TAG in definition:
                definition_details[ALIASES_TAG] = set(definition[ALIASES_TAG])
                for alias in definition[ALIASES_TAG]:
                    alias_name_normalized = self.normalize_name(alias)
                    self.definitions_by_name[alias_name_normalized] = definition_details

            self.definitions_by_name[definition_name_normalized] = definition_details
            self.definitions_by_id[definition[ID_TAG]] = definition_details

        self.modified = False

    def normalize_name(self, definition_name):
        name_normalized = str(definition_name).lower()
        name_normalized = re.sub('[ _*]', '', name_normalized)
        return name_normalized

    #  Returns dict containing definition data: name, id, desc and aliases (if any)
    def get_by_name(self, definition_string):
        definition = None
        definition_string_normalized = self.normalize_name(definition_string)
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

    def merge(self, new_definitions, auto_create: bool, auto_delete_list: list):
        if isinstance(new_definitions, list):
            self.merge_list(new_definitions, auto_create, auto_delete_list)
        else:
            raise ValueError("{type} data structure is not supported.".format(type=str(type(new_definitions))))

    def merge_list(self, new_definitions, auto_create: bool, auto_delete_list: list):
        i = 0
        for definition_name in new_definitions:
            self.merge_definition(i, definition_name, None, auto_create, auto_delete_list)
            i += 1

    def merge_definition(self, definition_id, definition_name, definition_desc, auto_create: bool, auto_delete_list: list):
        try:
            definition = self.get_by_id(definition_id)
            if definition_name in auto_delete_list:
                self.delete_definition(definition)
            else:
                self.update_definition(definition, definition_name, definition_desc)
        except ValueError:
            if definition_name not in auto_delete_list:
                self.create_definition(definition_id, definition_name, definition_desc, auto_create, auto_delete_list)

    def delete_definition(self, definition):
        existing_definition = self.definitions_by_id[definition[ID_TAG]]
        definition_name_normalized = self.normalize_name(existing_definition[NAME_TAG])
        self.definitions_by_name.pop(definition_name_normalized)
        self.definitions_by_id.pop(existing_definition[ID_TAG])

    def update_definition(self, definition, new_name, new_desc):
        if self.definition_changed(definition, new_name, new_desc):
            self.handle_definition_change(definition, new_name, new_desc)

    def handle_definition_change(self, definition, new_name, new_desc):
        new_definition = OrderedDict()
        new_definition[NAME_TAG] = new_name
        new_definition[DESCRIPTION_TAG] = new_desc
        decision = self.decision_maker.handle_change(definition, new_definition)
        if decision == DECISION_UPDATE:
            if new_name != definition[NAME_TAG]:
                modified = self.add_alias(definition, new_name)
                self.modified |= modified
            if new_desc is not None:
                definition[DESCRIPTION_TAG] = new_desc
                self.modified = True
        elif decision == DECISION_REPLACE:
            definition[NAME_TAG] = new_name
            if new_desc is not None:
                definition[DESCRIPTION_TAG] = new_desc
            else:
                definition.pop(DESCRIPTION_TAG, None)
            definition.pop(ALIASES_TAG, None)
            self.modified = True
        elif decision in (DECISION_REPLACE_NAME, DECISION_REPLACE_NAME_WITH_ALIAS):
            if decision == DECISION_REPLACE_NAME_WITH_ALIAS:
                self.add_alias(definition, definition[NAME_TAG])
            definition[NAME_TAG] = new_name
            self.modified = True
        elif decision == DECISION_DELETE:
            self.delete_definition(definition)
        # else DECISION_SKIP

    def add_alias(self, definition, new_name):
        modified = False
        if ALIASES_TAG in definition:
            aliases = definition[ALIASES_TAG]
            if new_name not in aliases:
                aliases.add(new_name)
                modified = True
        else:
            definition[ALIASES_TAG] = {new_name}
            modified = True
        return modified

    def definition_changed(self, definition, new_name, new_desc):
        name_normalized = self.normalize_name(definition[NAME_TAG])
        new_name_normalized = self.normalize_name(new_name)
        name_not_an_alias = ALIASES_TAG not in definition or new_name not in definition[ALIASES_TAG]
#        name_is_new = new_name != definition[NAME_TAG] and name_not_an_alias
        name_is_new = new_name_normalized != name_normalized and name_not_an_alias
        current_desc = definition[DESCRIPTION_TAG] if DESCRIPTION_TAG in definition else None
        description_is_new = new_desc is not None and new_desc != current_desc

        return name_is_new or description_is_new

    def create_definition(self, definition_id, definition_name, definition_desc, auto_create: bool, auto_delete_list: list):
        if definition_name not in auto_delete_list:
            definition_details = OrderedDict()
            definition_details[ID_TAG] = definition_id
            definition_details[NAME_TAG] = definition_name
            if definition_desc is not None:
                definition_details[DESCRIPTION_TAG] = definition_desc

            if auto_create or self.decision_maker.handle_new(definition_details) == DECISION_CREATE:
                self.handle_definition_creation(definition_details)

    def handle_definition_creation(self, definition_details):
        definition_name_normalized = self.normalize_name(definition_details[NAME_TAG])
        self.definitions_by_name[definition_name_normalized] = definition_details
        self.definitions_by_id[definition_details[ID_TAG]] = definition_details
        self.modified = True

    def dump(self):
        definition_list = []
        for definition_id in self.definitions_by_id:
            definition = self.definitions_by_id[definition_id]
            out_definition = {ID_TAG: definition[ID_TAG], NAME_TAG: definition[NAME_TAG]}
            if DESCRIPTION_TAG in definition:
                out_definition[DESCRIPTION_TAG] = definition[DESCRIPTION_TAG]
            if ALIASES_TAG in definition and definition[ALIASES_TAG] is not None:
                out_definition[ALIASES_TAG] = list(definition[ALIASES_TAG])
            definition_list.append(out_definition)
        return {self.definition_list_tag: definition_list}


