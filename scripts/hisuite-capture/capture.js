/* Experimental HiSuite 14 URL observer. See README.md before attaching. */
'use strict';

function makeUrlFilter(emit) {
  const tails = new Map();
  const seen = new Set();
  return {
    feed(key, chunk, complete = false) {
      if (!tails.has(key) && tails.size >= 64) tails.delete(tails.keys().next().value);
      const raw = (tails.get(key) || '') + chunk;
      const text = raw.replace(/\\\//g, '/');
      // A delimiter is required for streaming reads: do not print a partial path.
      const rx = /https?:\/\/(?:[a-z0-9-]+\.)+(?:dbankcdn|hicloud)\.(?:com|cn)(?::\d+)?\/(?:TDS\/data\/files|download\/data)\/[a-z0-9._~%+/-]+/gi;
      let m;
      while ((m = rx.exec(text)) !== null) {
        const end = m.index + m[0].length;
        if (m.index > 0 && /[a-z0-9.:/@-]/i.test(text[m.index - 1])) continue;
        if (m[0].length > 2048) continue;
        if (end === text.length ? !complete : !/[\s\x00-\x20"'<>?&#]/.test(text[end])) continue;
        // The regex excludes credentials, query strings and fragments.
        if (!seen.has(m[0]) && seen.size < 256) {
          seen.add(m[0]);
          emit(m[0]);
        }
      }
      if (complete) tails.delete(key);
      else tails.set(key, raw.slice(-8192));
    },
    clear() { tails.clear(); },
  };
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { makeUrlFilter };
} else {
  if (Process.platform !== 'windows' || Process.arch !== 'ia32' ||
      Process.enumerateModules()[0].name.toLowerCase() !== 'hisuite.exe') {
    throw new Error('Expected the 32-bit Windows HiSuite.exe process. No hooks installed.');
  }
  const filter = makeUrlFilter(url => console.log('PACKAGE_URL ' + url));
  const attached = new Set();
  const listeners = [];
  let stopped = false;
  const MAX_READ = 2 * 1024 * 1024;
  function scan(key, address, length, complete = false) {
    if (stopped || length <= 0 || length > MAX_READ || address.isNull()) return;
    try {
      const bytes = new Uint8Array(address.readByteArray(length));
      let s = '';
      // URLs are ASCII; do not try decoding arbitrary TLS plaintext as UTF-8.
      for (let i = 0; i < bytes.length; i += 4096) {
        s += String.fromCharCode.apply(null, bytes.subarray(i, i + 4096));
      }
      filter.feed(key, s, complete);
    } catch (_) { /* Unreadable memory is skipped; never print response data. */ }
  }
  function hook(mod, name, callbacks, label) {
    const address = mod.findExportByName(name);
    if (address === null || attached.has(address.toString())) return;
    try {
      listeners.push(Interceptor.attach(address, callbacks));
      attached.add(address.toString());
      console.log('READY ' + label);
    } catch (_) { console.log('SKIPPED one unavailable observer'); }
  }
  const observer = Process.attachModuleObserver({
    onAdded(mod) {
      if (stopped) return;
      if (mod.name.toLowerCase() === 'libssl-3.dll') {
        hook(mod, 'SSL_read', {
          onEnter(args) {
            this.key = 'ssl:' + args[0]; this.buf = args[1]; this.capacity = args[2].toInt32();
          },
          onLeave(retval) {
            const n = retval.toInt32();
            if (n > 0 && n <= this.capacity) scan(this.key, this.buf, n);
          },
        }, 'SSL_read');
        hook(mod, 'SSL_read_ex', {
          onEnter(args) {
            this.key = 'ssl:' + args[0]; this.buf = args[1];
            this.capacity = args[2].toUInt32(); this.count = args[3];
          },
          onLeave(retval) {
            if (retval.toInt32() !== 1) return;
            try {
              const n = this.count.readU32();
              if (n <= this.capacity) scan(this.key, this.buf, n);
            } catch (_) { /* No raw exception or memory content is logged. */ }
          },
        }, 'SSL_read_ex');
      }
      if (mod.name.toLowerCase() === 'httpcomponent.dll') {
        // Exact x86 thiscall export observed in Huawei's 14.0.0.380 installer.
        // this is ECX; args[2]/args[3] are char** output and int& output length.
        hook(mod, '?UnGzip@AppBaseHttpClient@NetWork@@AAEHPBDHPAPADAAH@Z', {
          onEnter(args) { this.output = args[2]; this.length = args[3]; },
          onLeave() {
            try { scan('gzip', this.output.readPointer(), this.length.readS32(), true); }
            catch (_) { /* Failure outputs can be unset. */ }
          },
        }, 'UnGzip');
      }
    },
  });
  function stop() {
    if (stopped) return;
    stopped = true;
    observer.detach();
    listeners.forEach(listener => listener.detach());
    filter.clear();
    console.log('STOPPED observers removed; close HiSuite to finish the helper.');
  }
  // Bound the observation window even if the operator leaves the helper open.
  setTimeout(stop, 5 * 60 * 1000);
  rpc.exports = { stop, dispose: stop };
  console.log('ACTIVE for up to five minutes. View version offers only.');
}
