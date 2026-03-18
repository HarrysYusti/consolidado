// src/utils/uuid.ts

/**
 * Genera un UUID v4 compatible con entornos seguros (HTTPS) e inseguros (HTTP IP).
 */
export function generateUUID(): string {
  // 1. Intento nativo (Mejor rendimiento, requiere HTTPS o localhost)
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }

  // 2. Plan B: Generación manual (Funciona en IPs locales HTTP)
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}