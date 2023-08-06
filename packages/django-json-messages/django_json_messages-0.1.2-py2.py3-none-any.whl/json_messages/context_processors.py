import django.contrib.messages

def json_messages(request):
  messages = django.contrib.messages.get_messages(request)
  return {
    'json_messages': map(lambda x: {'msg': str(x), 'type': x.tags}, messages)
  }