from collections import namedtuple
from dimagi.utils.decorators.memoized import memoized

from corehq.apps.app_manager.models import Module

class Lab(object):
    def __init__(self, name, description, used_in_module=None, used_in_form=None):
        self.name = name
        self.description = description

        self.used_in_module = used_in_module if used_in_module else lambda m: False
        self.used_in_form = used_in_form if used_in_form else lambda f: False

_LABS = {
    "case_detail_overwrite": Lab(
        name="Case Detail Overwrite",
        description="Ability to overwrite one case list or detail's settings with another's",
    ),
    "case_list_menu_item": Lab(
        name="Case List Menu Item",
        description="TODO",
        used_in_module=lambda m: isinstance(m, Module) and (m.case_list.show or m.task_list.show),  # TODO: will this break anything?
    ),
    "conditional_form_actions": Lab(
        name='Allow opening or closing bases based on a condition ("Only if the answer to...")',
        description="Allow changing form actions, deleting registration forms (TODO: rephrase?)",
        used_in_form=lambda f: f.actions.open_case.condition.type == 'if' or f.actions.close_case.condition.type, # TODO: will this break advanced forms?
    ),
    "display_conditions": Lab(
        name="Form and Menu Display Conditions",
        description="TODO",
        used_in_form=lambda f: bool(f.form_filter),
        used_in_module=lambda m: bool(m.module_filter),
    ),
    "edit_form_actions": Lab(
        name="Editing Form Actions",
        description="Allow changing form actions and deleting registration forms",
    ),
    "menu_mode": Lab(
        name="Menu Mode",
        description="TODO",
        used_in_module=lambda m: m.put_in_root,
    ),
    "register_from_case_list": Lab(
        name="Register from case list",
        description="TODO",
        used_in_module=lambda m: m.case_list_form.form_id, # TODO: break anything?
    ),
    "subcases": Lab(
        name="Child Cases",
        description="TODO",
        used_in_form=lambda f: bool(f.actions.subcases),    # TODO: will this break anything?
    ),
}

@memoized
def labs_by_name(app, slug):
    return {t['slug']: t for t in all_labs(app)}

@memoized
def all_labs(app, module=None, form=None):
    results = {}
    for slug, lab in _LABS.items():
        show = enabled = slug in app.labs and app.labs[slug]
        if form:
            show = show or lab.used_in_form(form)
        elif module:
            show = show or lab.used_in_module(module)
        results[slug] = {
            'slug': slug,
            'name': lab.name,
            'description': lab.description,
            'enabled': enabled,
            'show': show,
        }
    return results




'''
FEATURE PREVIEWS
Conditional Enum in Case List
Custom Calculations in Case List
Custom Single and Multiple Answer Questions
Icons in Case List
'''
