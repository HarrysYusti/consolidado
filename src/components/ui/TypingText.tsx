import  { useState, useEffect } from 'react';
import { Text } from '@chakra-ui/react';

interface TypingTextProps {
  text: string;
  instant?: boolean; // Nueva propiedad opcional
}

const TypingText = ({ text, instant = false }: TypingTextProps) => {
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
    }, 10);

    return () => clearTimeout(typingTimer);
  }, [displayedText, text]);

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
      {isTyping && <span className="typing-cursor">|</span>}
    </Text>
  );
};

export default TypingText;
