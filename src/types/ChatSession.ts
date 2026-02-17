export type ChatSession = {
  id: string;
  name: string;
  messages: ChatMessage[];
  timestamp: number;
};

export type ChatMessage = {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: number;
};
