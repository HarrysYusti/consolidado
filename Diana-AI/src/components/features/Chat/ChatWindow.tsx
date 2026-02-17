import { Box } from '@chakra-ui/react';
import React, { lazy, useEffect, useRef, useState } from 'react'; // Importa useEffect y useRef
import { useChat } from '@/hooks/features/Chat/useChat';
import ProgressBar from '@/components/ui/ProgressBar';

const ChatMessage = lazy(() => import('@/components/ui/ChatMessage'));

const ChatWindow: React.FC = (props) => {
  const { state } = useChat();
  const [progress, setProgress] = useState(false); //fake loading
  const [chatInstant, setChatInstant] = useState(false); //fake loading

  // Crea una referencia para el elemento al que queremos hacer scroll
  const endOfMessagesRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Si la referencia existe, haz scroll a ese elemento
    if (endOfMessagesRef.current) {
      endOfMessagesRef.current.scrollIntoView({ behavior: 'smooth' });
    }
    setChatInstant(false);
  }, [state.session?.messages, state.thinking]); // El efecto se ejecuta cuando cambia la lista de mensajes o el estado 'thinking'

  
  useEffect(() => {
    setProgress(state.hasInteraction); //fake loading si tiene mensajes
    setChatInstant(state.hasInteraction);
  }, [state.session?.id]);

  //fake loading
  useEffect(() => {
    if (progress) {
      const timer = setTimeout(() => {
        setProgress(false);
      }, 300);

      return () => clearTimeout(timer);
    }
  }, [progress]);

  return (
    <Box
      flex="1"
      overflowY="auto"
      px={6}
      py={6}
      display="flex"
      flexDirection="column"
      color="gray.300"
      bg={{ base: 'purple.50', _dark: 'gray.800' }}
      {...props}
    >
      {progress && (
        <ProgressBar/>
      )}
      {!progress &&
        state.session?.messages.map((msg, k) => (
          <ChatMessage
            key={k}
            msg={msg}
            clipboard={msg.role === 'assistant'}
            instant={!state.hasInteraction ? false : chatInstant}
          />
        ))}
      {state.thinking && (
        <ChatMessage
          msg={{ role: 'assistant', content: '' }}
          clipboard={false}
          spinner
        />
      )}
      {/* Elemento vacío al final para servir como punto de anclaje para el scroll */}
      <Box ref={endOfMessagesRef} />
    </Box>
  );
};

export default ChatWindow;
