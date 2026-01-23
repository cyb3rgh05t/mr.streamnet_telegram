/* eslint-disable react-refresh/only-export-components */
import {
  createContext,
  useContext,
  useRef,
  ReactNode,
  useCallback,
} from "react";

interface CacheEntry<T> {
  data: T;
  timestamp: number;
}

interface CacheContextType {
  get: <T>(key: string) => T | null;
  set: <T>(key: string, data: T, ttl?: number) => void;
  clear: (key?: string) => void;
  isStale: (key: string, ttl: number) => boolean;
}

const CacheContext = createContext<CacheContextType | undefined>(undefined);

const DEFAULT_TTL = 5 * 60 * 1000; // 5 minutes

export function CacheProvider({ children }: { children: ReactNode }) {
  const cacheRef = useRef<Map<string, CacheEntry<unknown>>>(new Map());

  const get = useCallback(<T,>(key: string): T | null => {
    const entry = cacheRef.current.get(key);
    if (!entry) return null;
    return entry.data as T;
  }, []);

  const set = useCallback(<T,>(key: string, data: T) => {
    cacheRef.current.set(key, {
      data,
      timestamp: Date.now(),
    });
  }, []);

  const clear = useCallback((key?: string) => {
    if (key) {
      cacheRef.current.delete(key);
    } else {
      cacheRef.current.clear();
    }
  }, []);

  const isStale = useCallback(
    (key: string, ttl: number = DEFAULT_TTL): boolean => {
      const entry = cacheRef.current.get(key);
      if (!entry) return true;
      return Date.now() - entry.timestamp > ttl;
    },
    [],
  );

  return (
    <CacheContext.Provider value={{ get, set, clear, isStale }}>
      {children}
    </CacheContext.Provider>
  );
}

export function useCache() {
  const context = useContext(CacheContext);
  if (!context) {
    throw new Error("useCache must be used within a CacheProvider");
  }
  return context;
}
