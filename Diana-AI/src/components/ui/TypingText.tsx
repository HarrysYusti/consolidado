import { useState, useEffect } from 'react';
import { Text } from '@chakra-ui/react';
import MarkdownRenderer from './MarkdownRenderer';

interface TypingTextProps {
  text: string;
  instant?: boolean;
  isMarkdown?: boolean;
}

const TypingText = ({ text, instant = false, isMarkdown = false }: TypingTextProps) => {
  const [displayedText, setDisplayedText] = useState('');
  const [isTyping, setIsTyping] = useState(true);

  useEffect(() => {
    if (instant) {
      setDisplayedText(text);
      setIsTyping(false);
    } else {
      setDisplayedText('');
      setIsTyping(true);
    }
  }, [text]);

  useEffect(() => {
    if (instant || displayedText === text) {
      setIsTyping(false);
      return;
    }

    const typingTimer = setTimeout(() => {
      setDisplayedText(text.slice(0, displayedText.length + 1));
    }, 1);

    return () => clearTimeout(typingTimer);
  }, [displayedText, text]);

  // Mensajes del asistente: renderiza Markdown en tiempo real durante el typing
  if (isMarkdown) {
    return (
      <>
        <MarkdownRenderer content={displayedText} />
      </>
    );
  }

  // Mensajes del usuario: texto plano con animación
  return (
    <Text
      as="span"
      color={{ base: 'black', _dark: 'white' }}
      _selection={{
        bg: 'orange.500',
        color: 'white',
      }}
    >
      {displayedText}
    </Text>
  );
};

export default TypingText;
