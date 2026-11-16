const { test } = require('node:test');
const assert = require('node:assert/strict');
const { workspaceUrl, sameOrigin } = require('./policy.cjs');
test('server choices preserve HTTPS and reject credential/URL execution schemes', () => {
  assert.equal(workspaceUrl('https://garda.example/'), 'https://garda.example/workspace');
  assert.equal(workspaceUrl('http://127.0.0.1:5173'), 'http://127.0.0.1:5173/workspace');
  for (const u of ['javascript:alert(1)', 'file:///private', 'http://remote.example', 'https://name:pass@garda.example', 'https://garda.example/?token=secret']) {
    assert.throws(() => workspaceUrl(u), undefined, u);
  }
});
test('navigation cannot escape the configured origin', () => {
  assert.equal(sameOrigin('https://garda.example/workspace/events', 'https://garda.example'), true);
  assert.equal(sameOrigin('https://garda.example.attacker.test', 'https://garda.example'), false);
  assert.equal(sameOrigin('https://garda.example:444', 'https://garda.example'), false);
});
