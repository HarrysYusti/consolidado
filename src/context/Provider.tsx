// src/Provider.jsx
import { ChakraProvider } from '@chakra-ui/react';
import { ChatProvider } from './ChatContext';
import { system } from '../theme';
import { ColorModeProvider } from '@/context/ColorMode';

interface ProviderProps {
  children: React.ReactNode;
}
const Provider: React.FC<ProviderProps> = ({ children }) => {
  return (
    <ChakraProvider value={system}>
      <ColorModeProvider>
        <ChatProvider>{children}</ChatProvider>
      </ColorModeProvider>
    </ChakraProvider>
  );
};

export default Provider;
