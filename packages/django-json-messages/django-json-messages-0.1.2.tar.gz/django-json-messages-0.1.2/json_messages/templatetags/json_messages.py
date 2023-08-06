from django import template
import json
import django.utils.html
import django.utils.safestring

register = template.Library()

@register.simple_tag(takes_context=True)
def json_messages(context):
	for m in context['json_messages']:
		m['msg'] = django.utils.html.escapejs(m['msg'])	
	json_dump = json.dumps(context['json_messages'])
	return json_dump

@register.simple_tag(takes_context=True)
def json_messages_script(context, on_window=True, js_variable='messages'):
	script = '<script type="text/javascript">{variable_definition} = {dump};</script>'
	if on_window:
		variable_definition = 'window.{}'
	else:
		variable_definition = 'var {}'

	variable_definition = variable_definition.format(js_variable)
	return script.format(variable_definition=variable_definition, dump=json_messages(context))
