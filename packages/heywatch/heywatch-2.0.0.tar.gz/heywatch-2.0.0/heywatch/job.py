import json
import os
import httplib2

USER_AGENT = 'HeyWatch/2.0.0 (Python)'

def submit(config_content, **kwargs):
  heywatch_url = os.getenv('HEYWATCH_URL', 'https://heywatch.com')
  api_key = os.getenv('HEYWATCH_API_KEY')

  if 'api_key' in kwargs:
    api_key = kwargs['api_key']

  h = httplib2.Http()
  h.add_credentials(api_key, '')

  headers = {'User-Agent': USER_AGENT, 'Content-Type': 'text/plain', 'Accept': 'application/json'}

  response, content = h.request(heywatch_url + '/api/v1/job', 'POST', body=config_content, headers=headers)

  return json.loads(content)