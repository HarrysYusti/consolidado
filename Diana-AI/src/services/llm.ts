/**
 * DIANA client service - ADAPTADO PARA N8N
 *
 * Conecta el Frontend de React con el Webhook de N8N.
 *
 * Mapeo de datos:
 * React (prompt)    -> N8N (message)
 * React (sessionId) -> N8N (sessionId)
 * N8N (respuesta)   -> React (answer)
 */

export type InferResponse = {
  answer: string;
  sessionId?: string;
};

// 1. CONFIGURACIÓN DE URL
// Tomamos la URL exacta del .env sin agregarle '/ask' porque N8N ya nos da la ruta completa.
const API_URL = (import.meta.env.VITE_API_BASE as string) || '';

/**
 * Envia una pregunta al workflow de N8N.
 */
export async function infer(
  prompt: string,
  sessionId?: string
): Promise<InferResponse> {

  // 2. PREPARACIÓN DEL PAQUETE (TRADUCCIÓN DE ENTRADA)
  // React tiene "prompt", pero N8N espera "message".
  // Si no hay sessionId, generamos uno temporal simple para que N8N no falle.
  const currentSessionId = sessionId || `user-${Date.now()}`;

  const body = {
    message: prompt,
    sessionId: currentSessionId
  };

  try {
    console.log("🚀 Enviando a N8N:", API_URL, body);

    const res = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // 'X-API-Key': ... (N8N webhooks públicos no suelen pedir API Key por defecto, lo quitamos por ahora)
      },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      throw new Error(`Error N8N: ${res.status} ${res.statusText}`);
    }

    // 3. PROCESAMIENTO DE RESPUESTA (TRADUCCIÓN DE SALIDA)
    const data = await res.json();
    console.log("✅ Respuesta de N8N:", data);

    // React espera "answer", pero N8N devuelve "respuesta" (según configuramos en el último nodo)
    return {
      answer: data.respuesta || "⚠️ N8N no devolvió el campo 'respuesta'. Revisa el nodo final.",
      sessionId: currentSessionId, // Mantenemos la sesión activa
    };

  } catch (error) {
    console.error('❌ Error fatal en infer():', error);
    return {
      answer: "Lo siento, hubo un problema de conexión con mi cerebro (N8N).",
      sessionId: sessionId,
    };
  }
}



/**DE AQUÍ PARA ABAJO ES EL CÓDIGO ANTIGUO   */
/**
 * DIANA client service
 * - Env vars:
 *    VITE_API_BASE: base URL (dev: '/api' -> proxy) | prod: 'https://host:8000'
 *    VITE_API_KEY:  API token for X-API-Key header
 * - Endpoint: POST {API_BASE}/ask  body: { question, session_id? }
 * - Response: { answer, references?, session_id }
 */
/**type LLMAskResponse = {
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
/**export async function infer(
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
}*/
