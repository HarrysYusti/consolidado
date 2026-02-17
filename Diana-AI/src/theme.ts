import { createSystem, defaultConfig, defineConfig } from '@chakra-ui/react';

const config = defineConfig({
  theme: {
    tokens: {
      colors: {
        diana: {
          200: { value: '#e9d5ff' },
          950: { value: '#302656ff' },
        },
      },
    },
  },
});

export const system = createSystem(defaultConfig, config);
