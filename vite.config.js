import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';
import tsconfigPaths from 'vite-tsconfig-paths';
import { VitePWA } from 'vite-plugin-pwa';
import { version } from './package.json';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tsconfigPaths(),
    VitePWA({
      registerType: 'autoUpdate',
      injectRegister: 'auto',
      workbox: {
        globPatterns: [
          '**/*.{js,css,html,ico,png,svg}'
        ],
      },
      devOptions: {
        enabled: true,
      },
      includeAssets: ['favicon.png', 'diana_192.png', 'diana_512.png'],
      manifest: {
        name: 'DIANA',
        short_name: 'DIANA',
        description:
          'Asistente digital IA para consultas administrativas sobre Natura',
        theme_color: '#302656ff',
        background_color: '#302656ff',
        display: 'standalone',
        start_url: '/',
        icons: [
          {
            src: 'diana_192.png',
            sizes: '192x192',
            type: 'image/png',
          },
          {
            src: 'diana_512.png',
            sizes: '512x512',
            type: 'image/png',
          },
        ],
      },
    }),
  ],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000', // IP del backend de Diana
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
  define: {
    __APP_VERSION__: JSON.stringify(version), // Define una variable global con la versión
  },
});
