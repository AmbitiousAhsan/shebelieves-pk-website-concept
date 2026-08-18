import { defineConfig } from 'vite';

// Relative base so the same `dist/` works at a domain root and under a
// GitHub Pages-style subpath without a rebuild. Bundled JS/CSS goes to
// `build/` so it never collides with the copied `public/assets/` tree.
export default defineConfig({
  base: './',
  build: {
    outDir: 'dist',
    assetsDir: 'build',
    target: 'es2020',
    cssTarget: 'chrome90',
    assetsInlineLimit: 0,
    sourcemap: false,
  },
  server: {
    host: '127.0.0.1',
    port: 5173,
  },
});
