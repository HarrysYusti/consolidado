import { ChatContext } from "@/context/ChatContext";
import { useContext } from "react";
import { ChatLogicHook } from "./_useChatLogic";

/**
 * Hook de React que encapsula toda la lógica de gestión del estado de chat.
 * @returns {ChatLogicHook} Un objeto con el estado y las acciones para interactuar con el chat.
 */
export const useChat = (): ChatLogicHook => {
  const context = useContext(ChatContext);
  if (!context) throw new Error('useChat debe usarse dentro de un ChatProvider');
  return context;
};
