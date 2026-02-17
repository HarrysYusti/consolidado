import { useEffect } from 'react';

export const useVoiceInput = (
  listening: boolean,
  onResult: (text: string) => void,
  onStop?: () => void
) => {
  useEffect(() => {
    const SpeechRecognition =
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) return;

    const recognition = new SpeechRecognition();
    recognition.lang = 'es-CL';
    recognition.interimResults = false;
    recognition.continuous = false;

    recognition.onresult = (event: any) => {
      const result = event.results[0][0].transcript;
      onResult(result);
    };

    recognition.onend = () => {
      onStop?.();
    };

    if (listening) {
      recognition.start();
    } else {
      recognition.stop();
    }

    return () => {
      recognition.abort();
    };
  }, [listening, onResult, onStop]);
};
