import { Flex } from '@chakra-ui/react';
import ChatWindow from '@/components/features/Chat//ChatWindow';
import ChatInput from '@/components/features/Chat//ChatInput';
import { useEffect } from 'react';
import { useChat } from '@/hooks/features/Chat/useChat';

function Main() {
  const { actions } = useChat();

  useEffect(() => {
    actions.newSession();
  }, []);

  return (
    <Flex direction="column" flex="1" overflow="hidden" >
      <ChatWindow />
      <ChatInput />
    </Flex>
  );
}

export default Main;
