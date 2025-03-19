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

# Makes sure that working directory is the add-on folder
abs_path = os.path.abspath(__file__)
path_of_this_file = os.path.dirname(abs_path)
os.chdir(path_of_this_file)

def open_settings(editor):
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
                deck_config.append([key_field_name, key])
            else:
                key = 0

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
        s11 = FieldSelector(nto, f"Select field in the note type {nto['name']} that contains search term")
        source_search_fields[nto["name"]] = s11.exec()

    new_entry["other_nt_search_fields"] = source_search_fields

    with open("config.json", "r") as file:
        user_config = json.load(file)

    user_config[editor_note_type["name"]] = new_entry

    with open("config.json", "w") as file:
        json.dump(user_config, file, indent=4)



def autopopulate(editor):
    """
    Automatically populates fields from notetype, in order determined by config.json.
    """


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