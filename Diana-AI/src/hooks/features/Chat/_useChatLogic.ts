import { ChatMessage, ChatSession } from '@/types/ChatSession';
import { ChatUseCase } from '@/usecases/chat';
import { SessionUseCase } from '@/usecases/session';
import { useEffect, useState } from 'react';

interface ChatState {
  session: ChatSession | undefined;
  history: ChatSession[];
  thinking: boolean;
  hasInteraction: boolean;
}

// Define una interfaz para las funciones de acción que serán devueltas
interface ChatActions {
  /**
   * Envía un mensaje de usuario a la IA y procesa la respuesta.
   * @param {string} message - El mensaje del usuario.
   */
  askQuestion: (value: string) => Promise<void>;
  clearHistory: () => void;
  /**
   * Carga una sesión del historial y la establece como la sesión actual.
   * Guarda la sesión actual en el historial antes de cargar la nueva.
   * @param {string} sessionId - El ID de la sesión del historial a cargar.
   */
  loadSessionFromHistory: (sessionId: string) => void;
  /**
   * Inicia una nueva sesión de chat. Guarda la sesión actual en el historial.
   */
  newSession: () => void;
  updateSessionName: (name: string) => string;
  /**
   * Agrega un nuevo mensaje a la sesión actual.
   * @param {string} content - El contenido del mensaje.
   * @param {'user' | 'assistant'} [role='user'] - El rol del remitente del mensaje.
   */
  addMessage: (content: string, role: 'user' | 'assistant') => void;
}

export interface ChatLogicHook {
  state: ChatState;
  actions: ChatActions;
}

const shortName = (name: string) => {
  return name.split(' ').slice(0, 5).join(' ');
};

/**
 * @internal This hook contains the internal logic for the ChatProvider.
 * It should not be used directly by components.
 * Use the `useChat` hook instead.
 */
export const _useChatLogic = (): ChatLogicHook => {
  const [session, setSession] = useState<ChatSession>();
  const [thinking, setThinking] = useState(false);
  const [history, setHistory] = useState<ChatSession[]>([]);

  /**
   * Actualiza el nombre de la sesión con un nombre acortado.
   * @param {string} name - El nombre a asignar a la sesión.
   */
  const updateSessionName = (name: string) => {
    const short = shortName(name);
    updateSession({ name: short });
    return short;
  };

  /**
   * Efecto que guarda la sesión en la persistencia cada vez que el estado de la sesión cambia.
   */
  useEffect(() => {
    if (session) {
      SessionUseCase.saveSession(session);
    }
  }, [session]);

  /**
   * Agrega un nuevo mensaje a la sesión actual.
   * @param {string} content - El contenido del mensaje.
   * @param {'user' | 'assistant'} [role='user'] - El rol del remitente del mensaje.
   */
  const addMessage = (content: string, role: 'user' | 'assistant' = 'user') => {
    if (!content.trim()) return;

    const newMessage: ChatMessage = {
      content,
      role,
      timestamp: Date.now(),
    };

    setSession((prevSession) => {
      let sessionToUpdate = prevSession;

      if (!prevSession) {
        const defaultSession = SessionUseCase.createNewSession();
        sessionToUpdate = { ...defaultSession, messages: [newMessage] };
      } else {
        sessionToUpdate = {
          ...prevSession,
          messages: [...prevSession.messages, newMessage],
        };
      }

      // Solo actualizar el nombre si es usuario y no hay nombre aún
      if (role === 'user' && !sessionToUpdate.name) {
        sessionToUpdate.name = shortName(content);
      }

      return sessionToUpdate;
    });
  };

  /**
   * Inicia una nueva sesión de chat. Guarda la sesión actual en el historial.
   */
  const newSession = () => {
    const newHistory = SessionUseCase.saveSessionInHistory(
      SessionUseCase.loadSession()
    );
    setHistory(newHistory);

    const initialMessage: ChatMessage = {
      content: ChatUseCase.getWelcomeMessage(),
      role: 'assistant',
      timestamp: Date.now(),
    };

    const newSession = SessionUseCase.createNewSession(initialMessage);
    setSession(newSession);
  };

  /**
   * Carga una sesión del historial y la establece como la sesión actual.
   * Guarda la sesión actual en el historial antes de cargar la nueva.
   * @param {string} sessionId - El ID de la sesión del historial a cargar.
   */
  const loadSessionFromHistory = (sessionId: string) => {
    const newSession = SessionUseCase.loadSessionFromHistory(sessionId);

    if (newSession) {
      const newHistory = SessionUseCase.saveSessionInHistory(session);
      setHistory(newHistory);

      setSession(newSession);
    }
  };

  const clearHistory = () => {
    setHistory([]);
    SessionUseCase.saveHistory([]);
  };

  /**
   * Envía un mensaje de usuario a la IA y procesa la respuesta.
   * @param {string} message - El mensaje del usuario.
   */
  const askQuestion = async (message: string) => {
    if (!message.trim()) return;

    addMessage(message.trim(), 'user');
    setThinking(true);

    const { answer, sessionId } = await ChatUseCase.askQuestion(
      message.trim(),
      session?.id
    );
    addMessage(answer, 'assistant');

    // Actualizamos ID de sesión si cambia
    setSession((prevSession) => {
      if (!prevSession) return undefined;
      if (prevSession.id !== sessionId && sessionId) {
        const updatedSession: ChatSession = { ...prevSession, id: sessionId };
        return updatedSession;
      }
      return prevSession;
    });
    setThinking(false);
  };

  const updateSession = (updates: Partial<ChatSession>) => {
    setSession((prevSession) => {
      if (!prevSession) {
        const defaultSession = SessionUseCase.createNewSession();
        return { ...defaultSession, ...updates };
      }

      const updatedSession = {
        ...prevSession,
        ...updates,
      };
      return updatedSession;
    });
  };

  const hasInteraction = session != undefined && session.messages.length > 1;

  return {
    state: { session, history, thinking, hasInteraction },
    actions: {
      askQuestion,
      clearHistory,
      loadSessionFromHistory,
      newSession,
      addMessage,
      updateSessionName,
    },
  };
};
