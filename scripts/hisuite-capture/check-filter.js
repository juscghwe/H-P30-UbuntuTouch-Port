'use strict';
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const { makeUrlFilter } = require('./capture.js');
const url = 'https://update.dbankcdn.com/TDS/data/files/p3/s15/G123/v456/f1/full/filelist.xml';
function run(chunks, complete = false) {
  const output = [];
  const f = makeUrlFilter(s => output.push(s));
  chunks.forEach((s, i) => f.feed('test', s, complete && i === chunks.length - 1));
  return output;
}
assert.deepEqual(run([url]), []);
assert.deepEqual(run([url], true), [url]);
assert.deepEqual(run(['"' + url + '?token=PRIVATE&serial=PRIVATE"']), [url]);
for (let cut = 1; cut < url.length; cut++) {
  assert.deepEqual(run([url.slice(0, cut), url.slice(cut) + '"']), [url]);
}
const escaped = url.replaceAll('/', '\\/');
for (let cut = 1; cut < escaped.length; cut++) {
  assert.deepEqual(run([escaped.slice(0, cut), escaped.slice(cut) + '"']), [url]);
}
assert.deepEqual(run([url + '" ' + url + '"']), [url]);
for (const bad of [
  'https://example.com/TDS/data/files/secret.zip',
  'https://dbankcdn.com.evil.example/TDS/data/files/secret.zip',
  'https://update.dbankcdn.com@evil.example/TDS/data/files/secret.zip',
  'https://user:password@update.dbankcdn.com/TDS/data/files/secret.zip',
  'https://update.dbankcdn.com/userdata/secret.zip',
  'email=private@example.com; serial=PRIVATE; SSID=PRIVATE',
]) assert.deepEqual(run([bad + '"'], true), []);
assert.deepEqual(run(['http://update.hicloud.com/download/data/test.zip#PRIVATE ']),
  ['http://update.hicloud.com/download/data/test.zip']);

// Exercise the actual Frida hook bodies with synthetic pointers, including the
// x86 thiscall output-reference positions, then verify that stop detaches them.
const hooks = new Map(); const logs = []; let observerDetached = false;
const api = {
  console: { log: s => logs.push(s) }, Uint8Array, String, Set, Map,
  Process: {
    platform: 'windows', arch: 'ia32', enumerateModules: () => [{ name: 'HiSuite.exe' }],
    attachModuleObserver(callbacks) {
      for (const name of ['libssl-3.dll', 'httpcomponent.dll']) {
        callbacks.onAdded({ name, findExportByName: n => n });
      }
      return { detach() { observerDetached = true; } };
    },
  },
  Interceptor: { attach(name, callbacks) {
    hooks.set(name, callbacks);
    return { detach() { hooks.delete(name); } };
  } },
  setTimeout() {}, rpc: {},
};
vm.runInNewContext(fs.readFileSync(__dirname + '/capture.js', 'utf8'), api);
function ptr(text) {
  return { isNull: () => false, readByteArray: n => Uint8Array.from(Buffer.from(text).subarray(0, n)).buffer };
}
function integer(n) { return { toInt32: () => n, toUInt32: () => n, readU32: () => n, readS32: () => n }; }
const body = url + '?private=PRIVATE"';
const ssl = hooks.get('SSL_read'); const ctx = {};
ssl.onEnter.call(ctx, ['socket1', ptr(body), integer(body.length)]);
ssl.onLeave.call(ctx, integer(body.length));
const gzip = hooks.get('?UnGzip@AppBaseHttpClient@NetWork@@AAEHPBDHPAPADAAH@Z');
const gzipBody = url.replace('filelist.xml', 'update.zip') + '"'; const gctx = {};
gzip.onEnter.call(gctx, [null, null, { readPointer: () => ptr(gzipBody) }, integer(gzipBody.length)]);
gzip.onLeave.call(gctx);
const ex = hooks.get('SSL_read_ex'); const ectx = {};
const exBody = url.replace('filelist.xml', 'update_full_base.zip') + '"';
ex.onEnter.call(ectx, ['socket2', ptr(exBody), integer(exBody.length), integer(exBody.length)]);
ex.onLeave.call(ectx, integer(1));
assert.deepEqual(logs.filter(s => s.startsWith('PACKAGE_URL ')),
  ['PACKAGE_URL ' + url, 'PACKAGE_URL ' + url.replace('filelist.xml', 'update.zip'),
    'PACKAGE_URL ' + url.replace('filelist.xml', 'update_full_base.zip')]);
assert(!logs.some(s => s.includes('PRIVATE')));
api.rpc.exports.stop();
assert(observerDetached); assert.equal(hooks.size, 0);
console.log('PASS: URL privacy, split/escaped reads, synthetic hook callbacks and cleanup');
