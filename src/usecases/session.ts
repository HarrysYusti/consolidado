import { ChatMessage, ChatSession } from '@/types/ChatSession';
import {
  loadHistory,
  loadSession,
  saveHistory,
  saveSession,
} from '@/services/session';

// Define el tipo para la interfaz del objeto.
interface SessionUseCaseType {
  loadSession: () => ChatSession | null;
  loadHistory: () => ChatSession[];
  saveSession: (session: ChatSession) => void;
  saveHistory: (history: ChatSession[]) => void;
  createNewSession: (initialMessage?: ChatMessage) => ChatSession;
  saveSessionInHistory: (
    session: ChatSession | null | undefined
  ) => ChatSession[];
  loadSessionFromHistory: (sessionId: string) => ChatSession | null;
}

export const SessionUseCase: SessionUseCaseType = {
  loadSession: (): ChatSession | null => {
    return loadSession();
  },

  loadHistory: () => {
    return loadHistory().sort((a, b) => b.timestamp - a.timestamp);
  },

  /**
   * Guarda una sesión en el almacenamiento local, limitando el número de mensajes.
   * @param {ChatSession} session La sesión a guardar.
   */
  saveSession: (session: ChatSession) => {
    const sessionToSave = {
      ...session,
      messages: session.messages.slice(-100),
    };
    saveSession(sessionToSave);
  },

  saveHistory: (history: ChatSession[]) => {
    const historyToSave = history.slice(0, 10);
    saveHistory(historyToSave);
  },

  /**
   * Crea y retorna una nueva sesión con un ID único.
   * @param {ChatMessage} [initialMessage] Un mensaje inicial opcional.
   * @returns {ChatSession} La nueva sesión creada.
   */
  createNewSession: (initialMessage?: ChatMessage) => {
    const newSession: ChatSession = {
      id: crypto.randomUUID(),
      name: '',
      timestamp: Date.now(),
      messages: initialMessage ? [initialMessage] : [],
    };

    return newSession;
  },

  /**
   * Guarda una sesión en el historial de sesiones.
   * @param {ChatSession | null | undefined} session La sesión a guardar.
   * @returns {ChatSession[]} El historial actualizado.
   */
  saveSessionInHistory: (
    session: ChatSession | undefined | null
  ): ChatSession[] => {
    const currentHistory = loadHistory();

    if (!session || session.messages.length <= 1) {
      return currentHistory;
    }

    const updatedHistory = currentHistory.filter((s) => s.id !== session.id);
    const historyWithNewSession = [
      { ...session, timestamp: Date.now() },
      ...updatedHistory,
    ];

    const historyToSave = historyWithNewSession.slice(0, 10);
    saveHistory(historyToSave);

    return historyToSave;
  },

  /**
   * Busca y carga una sesión del historial por su ID.
   * @param {string} sessionId El ID de la sesión a cargar.
   * @returns {ChatSession | null} La sesión encontrada o null si no se encuentra.
   */
  loadSessionFromHistory: (sessionId: string): ChatSession | null => {
    const currentHistory = loadHistory();
    const sessionToLoad = currentHistory.find((s) => s.id === sessionId);

    if (!sessionToLoad) {
      console.warn(`Sesión con ID ${sessionId} no encontrada.`);
    }

    return sessionToLoad || null;
  },
};
