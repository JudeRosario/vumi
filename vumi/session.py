# TODO definitly need a session object
# with hist & expiry & to_str & to_json etc
import yaml
import json
from vumi.errors import VumiError


class VumiSession():
    key = None
    decision_tree = None

    def __init__(self, **kwargs):
        pass

    def set_decision_tree(self, decision_tree):
        self.decision_tree = decision_tree

    def get_decision_tree(self):
        return self.decision_tree




class DecisionTree():
    pass


class TemplatedDecisionTree(DecisionTree):
    template = None

    def load_yaml_template(self, yaml_string):
        self.template = yaml.load(yaml_string)

    def get_template(self):
        return self.template


class PopulatedDesicionTree(TemplatedDecisionTree):
    data = None

    def load_json_data(self, json_string):
        self.data = json.loads(json_string)

    def get_data(self):
        return self.data

class TraversedDecisionTree(PopulatedDesicionTree):
    echo = False
    completed = False
    language = "english"
    template_current = None
    template_history = []
    # So that I can modify the original data, data_current must
    # be stored by reference as a list/dict, index/key pair
    data_current = ([None],0)
    data_history = []

    # The data will be a nested data-structure of a sort that can
    # be deserialized from a JSON string.

    # This means that when traversing it the current object will be one of:
    #     dict    -> in which case the template should auto-select the correct key
    #     list    -> in which case the user should be asked from displayed options
    #     boolean -> as for list, just yes/no questions only
    #     number  -> in which case the user should be prompted for a value
    #     string  -> in which case the user should be prompted for text

    # NB. User entered strings (which include things like dates),
        # should be avoided where possible.


    def resolve_dc(self):
        return self.data_current[0][self.data_current[1]]

    def select_dc(self, index_key):
        return (self.resolve_dc(), index_key)

    def update_dc(self, new_value):
        self.data_current[0][self.data_current[1]] = new_value



    def is_completed(self):
        return self.completed

    def echo_on(self):
        self.echo = True

    def set_language(self, language):
        self.language = language


    def dumps(self, level=1):
        s = ""
        if level >= 1:
            s += "\nTEMPLATE:\n"
            s += repr(self.template)
        if level >= 0:
            s += "\nTEMPLATE_CURRENT:\n "
            s += repr(self.template_current)
        if level >= 2:
            s += "\nTEMPLATE_HISTORY:\n"
            s += repr(self.template_history)
        if level >= 1:
            s += "\nDATA:\n"
            s += repr(self.data)
        if level >= 0:
            s += "\nDATA_CURRENT:\n"
            s += repr(self.data_current)
        if level >= 2:
            s += "\nDATA_HISTORY:\n"
            s += repr(self.data_history)
        return s


    def select(self, template, data):
        self.template_history.append(self.template_current)
        self.data_history.append(self.data_current)
        self.template_current = template
        self.data_current = data


    def previous(self):
        try:
            self.template_current = self.template_history.pop()
            self.data_current = self.data_history.pop()
        except:
            pass


    def start(self):
        if not self.template:
            raise VumiError("template must be loaded")
        if not self.data:
            raise VumiError("data must be loaded")
        t = self.template.get(self.template.get("__start__")["next"])
        d = (self.data, self.template.get("__start__")["next"])
        self.select(t, d)


    def question(self):
        que = ""
        que += self.template_current['question'][self.language]
        if type(self.resolve_dc()) == list:
            count = 0
            for opt in self.resolve_dc():
                count += 1
                que += "\n" + str(count) + ". " + opt.get(self.template_current['options'])
        if self.echo:
            print "\n", que
        if type(self.resolve_dc()) == list:
            print "######"
        return que


    def answer(self, ans):
        if self.echo:
            print ">", ans
        t = self.template.get(self.template_current.get("next"))
        if type(self.resolve_dc()) == list:
            d = (self.resolve_dc()[int(ans)-1],
                    self.template_current.get("next"))
            self.select(t, d)
        else:
            self.update_dc(ans)






