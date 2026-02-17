import { useState, useEffect } from 'react';

export const useOnlineStatus = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    // Agregamos los escuchadores de eventos al objeto window
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Limpiamos los escuchadores al desmontar el componente
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []); 

  return isOnline;
};