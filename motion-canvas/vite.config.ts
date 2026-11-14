import {defineConfig} from 'vite';
import motionCanvasModule from '@motion-canvas/vite-plugin';

// The published 3.17.2 plugin can be CommonJS-wrapped when Vite bundles ESM config.
// Normalize either module shape instead of assuming import.default is callable.
const wrapped = motionCanvasModule as unknown as {default?: typeof motionCanvasModule};
const motionCanvas = typeof motionCanvasModule === 'function'
  ? motionCanvasModule
  : wrapped.default;

if (typeof motionCanvas !== 'function') {
  throw new Error('Could not resolve Motion Canvas Vite plugin export');
}
export default defineConfig({plugins: [motionCanvas()]});
