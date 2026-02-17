import { infer } from '@/services/llm';
import { WELCOME_MESSAGES, ERROR_MESSAGES } from '@/constants/chatStrings';

// Define el tipo para la respuesta de la función askQuestion.
export interface ChatAnswerResponse {
  answer: string;
  sessionId: string | undefined;
}

// Define el tipo para el objeto ChatUseCase.
export interface ChatUseCaseType {
  getWelcomeMessage: () => string;
  askQuestion: (message: string, sessionId?: string) => Promise<ChatAnswerResponse>;
}

export const ChatUseCase: ChatUseCaseType = {
  getWelcomeMessage: (): string => {
    const randomIndex = Math.floor(Math.random() * WELCOME_MESSAGES.length);
    return WELCOME_MESSAGES[randomIndex];
  },

  askQuestion: async (message: string, sessionId?: string) => {
    try {
      const { answer, sessionId: newSessionId } = await infer(
        message,
        sessionId
      );
      return {
        answer: answer || ERROR_MESSAGES.NOT_FOUND,
        sessionId: newSessionId,
      };
    } catch (error) {
      console.error('Error al obtener respuesta:', error);
      return {
        answer: ERROR_MESSAGES.CONNECTION_FAILED,
        sessionId: sessionId,
      };
    }
  },
};
