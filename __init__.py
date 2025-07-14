from aqt import mw, gui_hooks
from aqt.qt import *
from aqt.utils import showInfo
import json
import os
from .util.DragDropSelector import DragDropSelector
from .util.FieldSelector import FieldSelector
from .util.NoteTypeSelector import NoteTypeSelector
from .util.CheckBoxSelector import CheckBoxSelector
from .util.KeyRestrictionSelector import KeyRestrictionSelector
from .util.DuplicateSelector import DuplicateSelector

# Makes sure that working directory is the add-on folder
abs_path = os.path.abspath(__file__)
path_of_this_file = os.path.dirname(abs_path)
os.chdir(path_of_this_file)

def open_settings(editor) -> None:
    """
    Opens the menu to configure autopopulate procedure for current note type and deck.
    """

    new_entry = {}  # Will be shoved into config.json with the note type name as the key

    # Gathering editor's current note type and list of fields in note type
    editor_note = editor.note
    editor_note_type = editor_note.model()
    current_fields = editor_note_type.get("flds", [])
    current_field_names = [field["name"] for field in current_fields]

    # Getting editor's current deck 
    # note: ONLY WORKS FOR NEW CARD MAKER EDITOR, NOT EXISTING CARD
    deck_id = editor.note.col.decks.current()["id"]
    deck_name = editor.note.col.decks.name(deck_id)
    new_entry["matching_deck"] = deck_name

    select_decks_from = mw.col.decks.all_names()
    select_decks_from.remove(deck_name)

    # Let user choose 1 or more source decks to copy from
    s1 = CheckBoxSelector("Select all decks to include in this configuration:", select_decks_from)
    source_decks = s1.exec()

    # Let user choose field of active note type that contains search term and fields to fill
    s2 = FieldSelector(editor_note_type, "Select the field that will contain the search term:")
    search_field_name = s2.exec()
    showInfo(search_field_name)
    new_entry["search_field"] = search_field_name

    # We will then be configuring stuff for the other fields only
    current_field_names.remove(search_field_name)
    s3 = CheckBoxSelector("Select all fields to be autofilled:", current_field_names)
    current_field_names = s3.exec()

    # Gather config for each field user wants to fill in
    ftf = {}
    all_nt_used = []

    for c_field in current_field_names:

        cf_config = []

        # Let user select source deck(s) for c_field
        s4 = CheckBoxSelector(f"Select all decks for the field {c_field}:", source_decks)
        c_deck_list = s4.exec()

        # Let user order the list for c_field
        s5 = DragDropSelector(f"Order the selection for the field {c_field}:", c_deck_list)
        c_deck_list = s5.exec()

        # For each source deck selected:
        for deck_name in c_deck_list:

            deck_config = [deck_name]

            # Let user select note type
            s6 = NoteTypeSelector(deck_name, c_field)
            note_type_name, ctr, kr = s6.exec()

            

            for nt in mw.col.models.all():
                if nt["name"] == note_type_name:
                    note_type_object = nt
                    break

            if note_type_object not in all_nt_used:
                all_nt_used.append(note_type_object)

            deck_config.append(note_type_name)
            
            # Give opportunity to allow card type restriction
            if ctr:
                card_type_names = [card["name"] for card in note_type_object["tmpls"]]
                s7 = CheckBoxSelector(f"Select all card types to search through in {note_type_name}", card_type_names)
                selected_ctn = s7.exec()
            else:
                selected_ctn = 0
            deck_config.append(selected_ctn)

            # Give opportunity to allow key restriction
            if kr:
                s8 = FieldSelector(note_type_object, "Select field that contains key:")
                key_field_name = s8.exec()
                s9 = KeyRestrictionSelector(deck_name, c_field, note_type_name, key_field_name)
                key = s9.exec()
                key_info = [key_field_name, key]
            else:
                key_info = 0
            deck_config.append(key_info)

            # Let user select field to copy from
            s10 = FieldSelector(note_type_object, f"Select field to copy from and into the field {c_field}:")
            field_to_copy_from = s10.exec()
            deck_config.append(field_to_copy_from)

            cf_config.append(deck_config)
    
        ftf[c_field] = cf_config
    new_entry["fields_to_fill"] = ftf

    # From all note types in config, select fields that contain search terms to match
    source_search_fields = {}
    for nto in all_nt_used:
        s11 = FieldSelector(nto, f"Select field in the note type {nto['name']} \nthat contains search term")
        source_search_fields[nto["name"]] = s11.exec()

    new_entry["other_nt_search_fields"] = source_search_fields

    with open("config.json", "r") as file:
        user_config = json.load(file)

    user_config[editor_note_type["name"]] = new_entry

    with open("config.json", "w") as file:
        json.dump(user_config, file, indent=4)


def autopopulate(editor) -> None:
    """
    Automatically populates fields as determined by config.json.
    """

    with open("config.json", "r") as file:
        user_config = json.load(file)

    # Getting current note type and config for the note type
    editor_note = editor.note   #  This object has the editor's fields which we can inject content into
    editor_note_type = editor_note.model()
    editor_note_type_name = editor_note_type["name"]
    nt_config = user_config[editor_note_type_name]

    # Getting the term to use to search
    nt_search_field_name = nt_config["search_field"]
    search_phrase = get_note_contents(nt_search_field_name, editor_note, editor_note_type)

    # Getting list of field configs
    fields_to_fill_dict = nt_config["fields_to_fill"]
    fields_to_fill_names = fields_to_fill_dict.keys()


    # Start filling one editor field at a time
    for f in fields_to_fill_names:
        field_config = fields_to_fill_dict[f]
        value = search_and_retrieve_value(nt_config, field_config, search_phrase)
        print("About to call put_value_into_editor")
        put_value_into_editor(f, value, editor, editor_note, editor_note_type)


def put_value_into_editor(target_field_name: str, value: str, editor, editor_note, editor_note_type):
    """Helper function to put a given string value into a specific field in the editor."""
    editor_note_fields = editor_note.fields  # List of strings of the values in editor
    nt_field_names = [f["name"] for f in editor_note_type["flds"]]
    print(editor_note_fields)
    print("value:" + value)
    num = 0
    for i, f in enumerate(nt_field_names):
        if f == target_field_name:
            num = i
            break
    print("index: " + str(num))
    editor_note_fields[num] = value
    editor.loadNote()        # Refresh editor UI

    
def get_note_contents(retrieval_field_name: str, note, note_type) -> str:
    """Helper function to retrieve the contents of a given field in the editor."""
    fields_list = note_type["flds"]
    field_name_list = []
    for field_object in fields_list:
        field_name_list.append(field_object["name"])
    for i, field_name in enumerate(field_name_list):
        if field_name == retrieval_field_name:
            index = i
    print(note.fields[index])
    return note.fields[index]


def search_and_retrieve_value(nt_config: dict, field_config: list, search_phrase: str) -> str:
    """
    Take entire config for one field and output a single value.
    If more than one result is found, let user choose which one to keep.
    If no value found, return an empty string.
    """
    for deck_config in field_config:
        deck_name = deck_config[0]
        deck_object = mw.col.decks.by_name(deck_name)
        nt_name = deck_config[1]
        card_types = deck_config[2]
        key_setting = deck_config[3]
        field_to_copy_from = deck_config[4]
        nt_search_field = nt_config["other_nt_search_fields"][nt_name]

        potential_card_ids = mw.col.find_cards(search_phrase)

        card_objects = []
        note_objects = []
        for i in potential_card_ids:
            card_objects.append(mw.col.get_card(i))

        for co in card_objects:
            source_note = mw.col.get_note(co.nid)
            valid = (
                co.did == deck_object["id"] and
                nt_name == co.note_type()["name"] and
                discriminate_ct(card_types, co) and
                discriminate_key(key_setting, co) and
                (get_note_contents(nt_search_field, source_note, source_note.model()) == search_phrase)
            )
            if valid:
                print("appending note:")
                print(source_note.fields)
                note_objects.append(source_note)

        if len(note_objects) == 0:
            print("no note objects found")
            continue
        elif len(note_objects) == 1:
            note = note_objects[0]
            return note[field_to_copy_from]
        else: # Handle duplicate in same source deck
            print("duplicates found in same deck")
            pass
    print("returning empty string")
    return ""
   

def discriminate_ct(card_types, co) -> bool:
    """Helper function to determine if card type restriction matches a card object."""
    if card_types == 0:
        return True
    
    for ct in card_types:
        template_index = co.ord

    if co.note_type()['tmpls'][template_index]['name'] == ct:
        return True
    else:
        return False
    

def discriminate_key(key_settings, co) -> bool:
    """Helper function to determine if key restriction matches a card object."""
    if key_settings == 0:
        return True
    
    key_field = key_settings[0]
    key = key_settings[1]
    note_object = mw.col.get_note(co.nid)

    if note_object[key_field] == key:
        return True
    else:
        return False
    

def add_editor_buttons(buttons, editor):
    """
    Add buttons to editor menu.
    """

    # get file paths for icons
    icon_settings_path = os.path.join(path_of_this_file, "icon_settings.png")
    icon_populate = os.path.join(path_of_this_file, "icon_populate.png")

    # editor button for changing copying procedure for notetype currently open
    settings_button = editor.addButton(
        icon = icon_settings_path,
        cmd = "quick_copy_from_premade_open_settings",
        func = open_settings,
        tip = "(Quick Copy From Premade) Configure population"
    )
    buttons.append(settings_button)

    # editor button for auto populate by cycling through configured notetypes
    populate_button = editor.addButton(
        icon = icon_populate,
        cmd = 'quick_copy_from_premade_autopopulate',
        func = autopopulate,
        tip="(Quick Copy From Premade) Automatically populate fields"
    )
    buttons.append(populate_button)


# Actually adds the buttons
gui_hooks.editor_did_init_buttons.append(add_editor_buttons)