import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';
import tsconfigPaths from 'vite-tsconfig-paths';
import { VitePWA } from 'vite-plugin-pwa';
import { version } from './package.json';

// https://vitejs.dev/config/
export default defineConfig({
  // 🟢 1. ESTO ES LO MÁS IMPORTANTE: Define la subcarpeta base
  base: './',

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
        // Aseguramos que el service worker navegue a la subcarpeta
        navigateFallback: '/diana/index.html',
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
        
        // 🟢 2. AJUSTE PWA: La app debe iniciar en la subcarpeta, no en la raíz
        start_url: '/diana/',
        scope: '/diana/', 
        
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
      // NOTA: Este proxy SOLO funciona en tu PC (npm run dev).
      // En el servidor IIS, este bloque es ignorado.
      '/api-n8n': {
        target: 'https://n8n-webhook.natura-coedados-dev.naturacloud.com', 
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api-n8n/, ''), 
        secure: false, 
      },
    },
  },
  define: {
    __APP_VERSION__: JSON.stringify(version),
  },
});
/*------------------------------------------------------------DE AQUÍ PARA ARRIBA ESTÁ EL CÓDIGO NUEVO-------------------------------------------- */
/*import react from '@vitejs/plugin-react';
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
          '**/
          /**.{js,css,html,ico,png,svg}'
        ],
      },/*
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
      // 🟢 AQUÍ ESTÁ EL CAMBIO (TÚNEL HACIA N8N)
      // Cualquier petición que empiece con '/api-n8n' será redirigida
      '/api-n8n': {
        target: 'https://n8n-webhook.natura-coedados-dev.naturacloud.com', // Dominio base de N8N
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api-n8n/, ''), // Borramos el prefijo antes de enviar
        secure: false, // Evita problemas de certificados SSL corporativos
      },
      
      // (Opcional) Dejo comentada la api anterior por si la necesitas en el futuro
      // '/api': {
      //   target: 'http://127.0.0.1:8000',
      //   changeOrigin: true,
      //   rewrite: (path) => path.replace(/^\/api/, ''),
      // },
    },
  },
  define: {
    __APP_VERSION__: JSON.stringify(version),
  },
});



/* --------------------------------------------DE AQUÍ PARA ABAJO ESTABA EL CÓDIGO ANTERIOR-------------------------------------------- */
/*import react from '@vitejs/plugin-react';
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
          '**/
          /**.{js,css,html,ico,png,svg}'
        ],
      },/*
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
*/
