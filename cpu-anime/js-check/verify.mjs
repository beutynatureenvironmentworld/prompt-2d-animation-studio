import {createRequire} from 'node:module';
const require = createRequire(import.meta.url);
const packages = ['three','remotion','@motion-canvas/core','@motion-canvas/2d'];
for (const name of packages) {
  const path = require.resolve(name);
  if (!path) throw new Error('Missing package: '+name);
  console.log('INSTALLED_LIBRARY', name, path);
}
console.log('JS_DEPENDENCY_SMOKE_PASS: packages resolve; no visual frames rendered with these libraries yet');
