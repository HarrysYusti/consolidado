/**
 * DIANA client service
 * - Env vars:
 *    VITE_API_BASE: base URL (dev: '/api' -> proxy) | prod: 'https://host:8000'
 *    VITE_API_KEY:  API token for X-API-Key header
 * - Endpoint: POST {API_BASE}/ask  body: { question, session_id? }
 * - Response: { answer, references?, session_id }
 */
type LLMAskResponse = {
  answer: string;
  references?: Array<Record<string, any>>;
  session_id?: string;
};

const API_BASE = (import.meta.env.VITE_API_BASE as string) || '/api';
const API_KEY = (import.meta.env.VITE_API_KEY as string) || '';

const API_URL = `${API_BASE.replace(/\/$/, '')}/ask`;

export type InferResponse = {
  answer: string;
  sessionId?: string;
};

/**
 * Envia una pregunta al backend de DIANA (/ask).
 * Mantiene contexto por session_id (si no hay, el backend lo genera y lo devuelve).
 */
export async function infer(
  prompt: string,
  sessionId?: string
): Promise<InferResponse> {
  const body: Record<string, any> = { question: prompt };
  if (sessionId) body.session_id = sessionId;

  const res = await fetch(API_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(API_KEY ? { 'X-API-Key': API_KEY } : {}),
    },
    body: JSON.stringify(body),
    credentials: 'include', // permite cookie de respaldo del SID si el backend la usa
  });

  const text = await res.text();
  let data: LLMAskResponse | any = {};
  try {
    data = JSON.parse(text);
  } catch {}

  if (!res.ok) {
    const msg =
      (data && (data.detail || data.error)) ||
      res.statusText ||
      'Error en DIANA';
    throw new Error(msg);
  }

  return {
    answer: data.answer,
    sessionId: data.session_id,
  };
}
