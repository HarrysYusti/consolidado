import { ChatMessage as ChatMessageType } from '@/types/ChatSession';
import {
  Box,
  Text,
  Image,
  Flex,
  Clipboard,
  IconButton,
  Spinner,
} from '@chakra-ui/react';
import { Tooltip } from './Tooltip';
import TypingText from './TypingText';

// Props tipadas para ChatMessage
interface ChatMessageProps {
  msg: ChatMessageType;
  clipboard?: boolean;
  spinner?: boolean;
  instant?: boolean;
}

const ChatMessage = ({
  msg,
  clipboard = false,
  spinner = false,
  instant = false,
}: ChatMessageProps) => {
  const isUser = msg.role === 'user';

  return (
    <Flex
      mb={4}
      align="flex-end"
      justify={isUser ? 'flex-end' : 'flex-start'}
      position="relative"
    >
      {!isUser && (
        <Image
          rounded="md"
          src="/diana.png"
          alt="DIANA"
          boxSize="30px"
          fit="cover"
          mr={2}
          mt={4}
          alignSelf="flex-start"
        />
      )}
      <Box
        position="absolute"
        top="4"
        left={isUser ? 'auto' : '32px'}
        right={isUser ? '-6px' : 'auto'}
        boxSize="6"
        bg={
          isUser
            ? { base: 'gray.300', _dark: 'gray.900' }
            : { base: 'diana.200', _dark: 'diana.950' }
        }
        transform="rotate(45deg)"
      />
      <Box
        bg={
          isUser
            ? { base: 'gray.300', _dark: 'gray.900' }
            : { base: 'diana.200', _dark: 'diana.950' }
        }
        color="gray.100"
        p={4}
        borderRadius="lg"
        maxW={{ base: '90%', lg: '70%' }}
        mb={2}
        zIndex={2}
      >
        {spinner && (
          <Spinner
            size="xs"
            mt={1}
            color={{ base: 'black', _dark: 'white' }}
            alignSelf="flex-start"
          />
        )}
        <TypingText text={msg.content} instant={isUser || instant} />
        {clipboard && (
          <Clipboard.Root value={msg.content}>
            <Tooltip content="Copiar">
              <Clipboard.Trigger asChild>
                <IconButton
                  size="2xs"
                  mt={1}
                  alignSelf="flex-start"
                  bg="transparent"
                  color={{ base: 'black', _dark: 'white' }}
                >
                  <Clipboard.Indicator />
                </IconButton>
              </Clipboard.Trigger>
            </Tooltip>
          </Clipboard.Root>
        )}
      </Box>
    </Flex>
  );
};

export default ChatMessage;
