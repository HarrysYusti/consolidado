import {
  VStack,
  HStack,
  IconButton,
  Button,
  Text,
  Dialog,
  Portal,
  CloseButton,
  useEditable,
  Editable,
} from '@chakra-ui/react';
import { MdAddCircleOutline } from 'react-icons/md';

import { FaEdit, FaTrashAlt } from 'react-icons/fa';
import { useEffect, useState } from 'react';
import { useChat } from '@/hooks/features/Chat/useChat';

interface SidebarContentProps {
  isExpanded: boolean;
  callWithAction?: (action: string) => void;
}

const ChatPanelControl = ({
  isExpanded,
  callWithAction,
}: SidebarContentProps) => {
  const { state, actions } = useChat();

  const newChat = () => {
    if (state.hasInteraction) {
      actions.newSession();
    }
    callWithAction?.('new');
  };

  return (
    <VStack align="strech" w={'300px'}>
      {/* Nuevo Chat */}
      <Button
        onClick={newChat}
        variant="ghost"
        justifyContent={'flex-start'}
        color="gray.300"
        size="md"
        px={4}
        my={6}
        disabled={state.thinking}
        _hover={{ bg: 'purple.950' }}
        rounded="full"
      >
        <HStack>
          <MdAddCircleOutline />
          {isExpanded && <Text>Nuevo Chat</Text>}
        </HStack>
      </Button>

      {/* Actual */}
      {isExpanded && <CurrentChat />}

      {/* Historial */}
      {isExpanded && state.history.length != 0 && (
        <ChatHistorial callWithAction={callWithAction} />
      )}
    </VStack>
  );
};

export default ChatPanelControl;

const CurrentChat = () => {
  const { state, actions } = useChat();

  const [isTriggered, setIsTriggered] = useState(false);

  //Quita el efecto parpadeo
  useEffect(() => {
    if (isTriggered) {
      const timer = setTimeout(() => {
        setIsTriggered(false);
      }, 400);

      return () => clearTimeout(timer);
    }
  }, [isTriggered]);

  const editable = useEditable({
    defaultValue: state.session?.name,
  });

  useEffect(() => {
    editable.setValue(state.session?.name || 'Sin nombre');
    setIsTriggered(true);
  }, [state.session?.name, state.session?.id]);

  const updateName = () => {
    if (editable.editing) {
      if (editable.value) {
        const newName = actions.updateSessionName(editable.value);
        editable.setValue(newName);
        setIsTriggered(true);
      } else {
        editable.setValue(state.session?.name || 'Sin nombre');
      }
    }
  };

  return (
    <VStack
      align="strech"
      px={4}
      pt={2}
      overflowY="hidden"
      justifyContent="flex-start"
    >
      <Text fontSize="sm" fontWeight="bold" color="gray.400" mb={2}>
        Chat actual
      </Text>
      {!state.hasInteraction && (
        <Text
          justifyContent="flex-start"
          color="gray.100"
          fontSize="sm"
          whiteSpace="nowrap"
          overflow="hidden"
          textOverflow="ellipsis"
          lineClamp="1"
          animation={isTriggered ? 'pulse' : ''}
          animationDuration={'slow'}
          py={1}
        >
          Pregunta lo que quieras...
        </Text>
      )}
      {state.hasInteraction && (
        <Editable.RootProvider value={editable} unstyled onBlur={updateName}>
          <Editable.Preview
            justifyContent="flex-start"
            color="gray.100"
            fontSize="sm"
            whiteSpace="nowrap"
            overflow="hidden"
            textOverflow="ellipsis"
            lineClamp="1"
            animation={isTriggered ? 'pulse' : ''}
            animationDuration={'slow'}
            cursor="pointer"
            py={1}
          />
          <HStack justifyContent="flex-start" align="strech">
            <Editable.Input
              justifyContent="flex-start"
              color="gray.100"
              fontSize="sm"
              bg={'diana.950'}
              focusRing={'none'}
              w={'100%'}
              py={1}
              flex={'1'}
            />
            {editable.editing && (
              <IconButton
                aria-label="Modificar"
                size={'2xs'}
                color={'gray.400'}
                rounded="full"
                variant="ghost"
                _hover={{ bg: 'purple.950' }}
                mt={'2px'}
              >
                <FaEdit />
              </IconButton>
            )}
          </HStack>
        </Editable.RootProvider>
      )}
    </VStack>
  );
};

const ChatHistorial = ({
  callWithAction,
}: {
  callWithAction?: (action: string) => void;
}) => {
  const { state, actions } = useChat();

  const [confirmDelete, setConfirmDelete] = useState(false);

  const loadSession = (sessionId: string) => {
    actions.loadSessionFromHistory(sessionId);
    callWithAction?.('load');
  };

  const clearHistory = () => {
    setConfirmDelete(false);
    actions.clearHistory();
  };

  return (
    <VStack align="strech" px={4} pt={2}>
      <HStack justifyContent="flex-start" align="strech">
        <Text
          justifyContent="flex-start"
          fontSize="sm"
          fontWeight="bold"
          color="gray.400"
          w={'100%'}
          mb={2}
          lineClamp="1"
        >
          Chat recientes (este navegador)
        </Text>
        <IconButton
          aria-label="Eliminar"
          size={'2xs'}
          color={'gray.400'}
          onClick={() => setConfirmDelete(true)}
          hidden={state.history.length === 0}
          disabled={state.thinking}
          rounded="full"
          variant="ghost"
          _hover={{ bg: 'purple.950' }}
        >
          <FaTrashAlt />
        </IconButton>
      </HStack>

      <VStack align="strech" px={4} pt={2} maxH="450px" overflowY="auto">
        {state.history.map(
          (chat, key) =>
            state.session?.id != chat.id && (
              <Button
                key={key}
                variant="ghost"
                size="sm"
                color="gray.400"
                onClick={() => {
                  loadSession(chat.id);
                }}
                justifyContent="flex-start"
                disabled={state.thinking}
                p={1}
                rounded="full"
                _hover={{ bg: 'purple.950' }}
              >
                <Text
                  fontSize="sm"
                  whiteSpace="nowrap"
                  textOverflow="ellipsis"
                  lineClamp="1"
                  as="span"
                  textAlign="left"
                >
                  {chat.name}
                </Text>
              </Button>
            )
        )}
      </VStack>
      <Dialog.Root
        role="alertdialog"
        lazyMount
        open={confirmDelete}
        onOpenChange={(e) => setConfirmDelete(e.open)}
      >
        <Portal>
          <Dialog.Backdrop />
          <Dialog.Positioner>
            <Dialog.Content>
              <Dialog.Header>
                <Dialog.Title>Quieres eliminar el historial?</Dialog.Title>
              </Dialog.Header>
              <Dialog.Footer>
                <Dialog.ActionTrigger asChild>
                  <Button variant="outline">Cancelar</Button>
                </Dialog.ActionTrigger>
                <Button colorPalette="red" onClick={clearHistory}>
                  Eliminar
                </Button>
              </Dialog.Footer>
              <Dialog.CloseTrigger asChild>
                <CloseButton size="sm" />
              </Dialog.CloseTrigger>
            </Dialog.Content>
          </Dialog.Positioner>
        </Portal>
      </Dialog.Root>
    </VStack>
  );
};
