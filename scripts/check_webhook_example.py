"""Exercise the published Python example against captured production-signer fixtures."""
import json
from pathlib import Path
import re
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / 'docs/cloud/guides/webhooks.mdx'
FIXTURES = json.loads((ROOT / 'scripts/fixtures/webhook-signatures.json').read_text())
namespace = {}
code = next(block for block in re.findall(r'```python[^\n]*\n(.*?)```', DOC.read_text(), re.S)
            if 'def verify_webhook(' in block)
exec(compile(code, str(DOC), 'exec'), namespace)
verify = namespace['verify_webhook']


class WebhookExampleTests(unittest.TestCase):
    def test_signer_vectors_and_tampering(self):
        for item in FIXTURES['vectors']:
            with self.subTest(vector=item['name']), patch('time.time', return_value=int(item['timestamp'])):
                args = [item['body'].encode(), item['signature'], item['timestamp'], FIXTURES['secret']]
                self.assertTrue(verify(*args))
                self.assertFalse(verify(args[0].replace(b'synthetic-session', b'other-session'), *args[1:]))
                self.assertFalse(verify(*args[:3], 'wrong-secret'))
                # HTTP whitespace/key order is not what is signed.
                reordered = dict(reversed(list(json.loads(item['body']).items())))
                self.assertTrue(verify(json.dumps(reordered, indent=2).encode(), *args[1:]))

    def test_bad_headers_and_json_return_false(self):
        item = FIXTURES['vectors'][0]
        args = [item['body'].encode(), item['signature'], item['timestamp'], FIXTURES['secret']]
        with patch('time.time', return_value=int(item['timestamp'])):
            for signature in ['', 'a', 'gg' * 32, 'é' * 64, None]:
                self.assertFalse(verify(args[0], signature, *args[2:]))
            for timestamp in ['', 'NaN', '1e9', item['timestamp'] + 'junk', None, '0', str(int(item['timestamp']) + 301)]:
                self.assertFalse(verify(*args[:2], timestamp, args[3]))
            for body in [b'{', b'null', b'[]', b'\xff', b'{"value":NaN}']:
                self.assertFalse(verify(body, *args[1:]))
        with patch('time.time', return_value=int(item['timestamp']) + 301):
            self.assertFalse(verify(*args))


if __name__ == '__main__':
    unittest.main()
