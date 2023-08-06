import collections

__author__ = 'maartenbreddels'


def get_option(map, name, default, alias_list):

option_groups = collections.defaultdict(lambda: collections.defaultdict(dict))
OptionType = collections.namedtuple("OptionType", ["name", "type", "validator"])

def define_option(group, name, type, validator):
	option_groups[group][name] = OptionType(name, type, validator)

class Options(dict):
	def __init__(self, group_list, **kwargs):
		for name, value in kwargs:


	@classmethod
	def from_cmdline(group_list, **kwargs):
		pass