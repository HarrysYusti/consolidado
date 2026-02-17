import { _useChatLogic } from "@/hooks/features/Chat/_useChatLogic";
import { createContext, ReactNode, useContext } from "react";


export const ChatContext = createContext<ReturnType<typeof _useChatLogic> | undefined>(undefined);

interface ChatProviderProps { children: ReactNode; }

export const ChatProvider = ({ children }: ChatProviderProps) => {
  const chat = _useChatLogic();
  return <ChatContext.Provider value={chat}>{children}</ChatContext.Provider>;
};