import re
import yaml
from wled_constants import NAME_TAG, ID_TAG, DESCRIPTION_TAG, ALIASES_TAG


class WledDefinitions:

    def __init__(self, definitions_file: str, definition_list_tag: str):
        with open(definitions_file) as f:
            self.definition_data = yaml.safe_load(f)

        self.definitions_by_name = {}
        self.definitions_by_id = {}
        for definition in self.definition_data[definition_list_tag]:
            definition_name_normalized = self.normalize_definition_name(definition[NAME_TAG])
            definition_details = {NAME_TAG: definition[NAME_TAG], ID_TAG: definition[ID_TAG],
                                  DESCRIPTION_TAG: definition[DESCRIPTION_TAG]}

            if ALIASES_TAG in definition:
                definition_details[ALIASES_TAG] = definition[ALIASES_TAG]
                for alias in definition[ALIASES_TAG]:
                    alias_name_normalized = self.normalize_definition_name(alias)
                    self.definitions_by_name[alias_name_normalized] = definition_details

            self.definitions_by_name[definition_name_normalized] = definition_details
            self.definitions_by_id[definition[ID_TAG]] = definition_details

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

    def modify_definition(self, definition_id, definition_name, definition_desc):
        try:
            definition = self.get_definition_by_id(definition_id)
            self.update_definition(definition, definition_name, definition_desc)
        except ValueError:
            self.add_definition(definition_id, definition_name, definition_desc)
        pass

    def update_definition(self, definition, definition_name, definition_desc):
        if definition_name != definition[NAME_TAG]:
            if ALIASES_TAG in definition:
                aliases = definition[ALIASES_TAG]
                aliases.add(definition_name)
            else:
                definition[ALIASES_TAG] = set(definition_name)

        if definition_desc is not None:
            definition[DESCRIPTION_TAG] = definition_desc

    def add_definition(self, definition_id, definition_name, definition_desc):
        definition_name_normalized = self.normalize_definition_name(definition_name)
        definition_details = {NAME_TAG: definition_name_normalized, ID_TAG: definition_id,
                              DESCRIPTION_TAG: definition_desc}

        self.definitions_by_name[definition_name_normalized] = definition_details
        self.definitions_by_id[definition_id] = definition_details


