import { ChatSession } from '@/types/ChatSession'; // Asegúrate de la ruta correcta
import { getItem, setItem } from '@/utils/storage';

const HISTORY_KEY = 'chatHistory';
const CHAT_KEY = 'chatSession';

export function loadHistory(): ChatSession[] {
  const history = getItem<ChatSession[]>(HISTORY_KEY);
  return Array.isArray(history) ? history : [];
}

export function saveHistory(history: ChatSession[]): void {
  setItem(HISTORY_KEY, history);
}

export function loadSession(): ChatSession | null {
  const session = getItem<ChatSession>(CHAT_KEY);
  return session;
}

export function saveSession(session: ChatSession): void {
  setItem(CHAT_KEY, session);
}
