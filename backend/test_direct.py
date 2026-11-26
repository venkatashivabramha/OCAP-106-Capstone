import os, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
django.setup()
from django.test import Client
import json
c = Client()
passed = []; failed = []

def t(label, method, url, data=None, token=None):
    kw = {'content_type': 'application/json'}
    if token: kw['HTTP_AUTHORIZATION'] = 'Bearer ' + token
    try:
        fn = getattr(c, method.lower())
        r = fn(url, data=json.dumps(data) if data is not None else None, **kw)
        sc = r.status_code
        try: body = r.json()
        except: body = {}
        if sc < 400: passed.append('PASS ['+str(sc)+'] '+label); return body
        failed.append('FAIL ['+str(sc)+'] '+label+': '+str(body)[:150]); return None
    except Exception as e:
        import traceback; traceback.print_exc()
        failed.append('FAIL [EXC] '+label+': '+str(e)[:150]); return None

r = t('send-otp','POST','/api/auth/send-otp/',{'phone_number':'+919876543210'})
if r: passed[-1] += ' -> ' + r.get('message','?')
r = t('verify-otp','POST','/api/auth/verify-otp/',{'phone_number':'+919876543210','otp':'123456'})
tok = r.get('access_token') if r else None
if r: passed[-1] += ' -> uid=' + str(r.get('user_id')) + ' token=' + ('OK' if tok else 'MISSING')
r = t('profile','GET','/api/auth/profile/',None,tok)
if r: passed[-1] += ' -> ' + str(r.get('phone_number','?'))
r = t('provider-status','GET','/api/llm/provider-status/')
if r: passed[-1] += ' -> available=' + str(r.get('available')) + ' primary=' + str(r.get('primary'))
r = t('isl-chat','POST','/api/llm/isl-chat/',{'text':'hello','signs':['HELLO']},tok)
if r: passed[-1] += ' -> [' + r.get('provider','?') + '] ' + r.get('bot_response','')[:60]
r = t('sign-seq','POST','/api/recognition/sequence/',{'sign_label':'HELLO','confidence':0.9},tok)
if r: passed[-1] += ' -> seq=' + str(r.get('current_sequence'))
r = t('sign-flush','POST','/api/recognition/flush/',{},tok)
if r: passed[-1] += ' -> sentence=' + str(r.get('sentence_text'))
r = t('speak','POST','/api/llm/speak/',{'text':'Hello'},tok)
if r: passed[-1] += ' -> provider=' + r.get('provider','?') + ' audio=' + ('yes' if r.get('audio_b64') else 'browser_fallback')
r = t('history','GET','/api/llm/history/',None,tok)
if r: passed[-1] += ' -> ' + str(r.get('total',0)) + ' msgs'
r = t('conversations','GET','/api/conversations/',None,tok)
print()
print('='*55)
print('RESULTS: ' + str(len(passed)) + ' PASSED  ' + str(len(failed)) + ' FAILED')
print('='*55)
[print(x) for x in passed]
[print(x) for x in failed]
print('='*55)
