import { Flex, Input, IconButton, Spinner } from '@chakra-ui/react';
import React, { lazy, Suspense, useState } from 'react';
import { FaMicrophone, FaStop } from 'react-icons/fa';
import { IoSend } from 'react-icons/io5';
import { useVoiceInput } from '@/hooks/utils/useVoiceInput';
import { Tooltip } from '@/components/ui/Tooltip';
import { useOnlineStatus } from '@/hooks/utils/useOnlineStatus';
import { useChat } from '@/hooks/features/Chat/useChat';

const EasterEgg = lazy(() => import('@/components/ui/EasterEgg'));

const ChatInput = () => {
  const [message, setMessage] = useState<string>('');
  const { state, actions } = useChat();
  const [listening, setListening] = useState<boolean>(false);
  const isOnline = useOnlineStatus();

  const [showEasterEgg, setShowEasterEgg] = useState(false);

  const handleSend = async () => {
    setListening(false);
    //easter egg
    if (isKonamiCode(message)) {
      setShowEasterEgg(true);
    } else {
      await actions.askQuestion(message);
    }

    setMessage('');
  };
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  useVoiceInput(
    listening,
    (text) => setMessage((prev) => prev + ' ' + text),
    () => setListening(false)
  );

  return (
    <Flex
      p={4}
      bg={{ base: 'purple.100', _dark: 'gray.900' }}
      align="center"
      borderTop="1px solid"
      borderColor={{ base: 'gray.100', _dark: 'gray.700' }}
    >
      {isOnline && (
        <>
          <Input
            placeholder="Pregunta lo que quieras..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            bg={{ base: 'gray.100', _dark: 'gray.700' }}
            borderRadius="full"
            mr={4}
            color={{ base: 'black', _dark: 'white' }}
            _placeholder={{ color: 'gray.400' }}
            disabled={state.thinking}
          />
          <Tooltip content="Grabar">
            <IconButton
              aria-label="Grabar"
              mr={2}
              disabled={state.thinking}
              color={{ base: 'diana.950', _dark: 'diana.200' }}
              rounded="full"
              variant="ghost"
              _hover={{ bg: { base: 'gray.100', _dark: 'gray.700' } }}
              onClick={() => setListening((prev) => !prev)}
            >
              {listening ? <FaStop /> : <FaMicrophone />}
            </IconButton>
          </Tooltip>

          <Tooltip content="Enviar">
            <IconButton
              aria-label="Enviar"
              mr={2}
              disabled={state.thinking}
              color={{ base: 'diana.950', _dark: 'diana.200' }}
              rounded="full"
              variant="ghost"
              _hover={{ bg: { base: 'gray.100', _dark: 'gray.700' } }}
              onClick={handleSend}
            >
              {!state.thinking ? <IoSend /> : <Spinner />}
            </IconButton>
          </Tooltip>
          <Suspense>
            <EasterEgg show={showEasterEgg} />
          </Suspense>
        </>
      )}
    </Flex>
  );
};

export default ChatInput;

const KONAMI_CODE = 'td';

const isKonamiCode = (message: string): boolean => {
  const msg = message.toLowerCase().replace(/,|\s/g, '').trim();
  return msg == KONAMI_CODE;
};
