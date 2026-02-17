/**
 * A generic helper function to get data from localStorage safely.
 * @param key The localStorage key.
 * @returns The parsed data or null if an error occurs.
 */
export function getItem<T>(key: string): T | null {
  try {
    const storedItem = localStorage.getItem(key);
    if (!storedItem) {
      return null;
    }
    const parsedItem = JSON.parse(storedItem) as T;
    // You could add runtime validation here, e.g., using Zod.
    return parsedItem;
  } catch (error) {
    console.error(`Error loading key "${key}" from localStorage:`, error);
    return null;
  }
}

/**
 * A generic helper function to set data to localStorage safely.
 * @param key The localStorage key.
 * @param data The data to store.
 */
export function setItem<T>(key: string, data: T): void {
  try {
    const serializedData = JSON.stringify(data);
    localStorage.setItem(key, serializedData);
  } catch (error) {
    console.error(`Error saving key "${key}" to localStorage:`, error);
  }
}