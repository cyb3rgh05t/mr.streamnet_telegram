/* eslint-disable react-refresh/only-export-components */
import {
  createContext,
  useContext,
  ReactNode,
  useCallback,
  useEffect,
  useState,
} from "react";

interface CacheEntry<T> {
  data: T;
  timestamp: number;
}

interface CacheContextType {
  get: <T>(key: string) => T | null;
  set: <T>(key: string, data: T, ttl?: number) => void;
  clear: (key?: string) => void;
  remove: (key: string) => void;
  isStale: (key: string, ttl: number) => boolean;
}

const CacheContext = createContext<CacheContextType | undefined>(undefined);

const DEFAULT_TTL = 5 * 60 * 1000; // 5 minutes
const CACHE_PREFIX = "tg_bot_cache_";

// Helper to get all cache keys
const getCacheKeys = (): string[] => {
  const keys: string[] = [];
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (key?.startsWith(CACHE_PREFIX)) {
      keys.push(key.replace(CACHE_PREFIX, ""));
    }
  }
  return keys;
};

export function CacheProvider({ children }: { children: ReactNode }) {
  const [isReady, setIsReady] = useState(false);

  // Clean up expired cache entries on mount
  useEffect(() => {
    try {
      const keys = getCacheKeys();
      const now = Date.now();
      const maxAge = 24 * 60 * 60 * 1000; // 24 hours max age for any cache

      keys.forEach((key) => {
        try {
          const raw = localStorage.getItem(CACHE_PREFIX + key);
          if (raw) {
            const entry = JSON.parse(raw);
            if (now - entry.timestamp > maxAge) {
              localStorage.removeItem(CACHE_PREFIX + key);
            }
          }
        } catch {
          localStorage.removeItem(CACHE_PREFIX + key);
        }
      });
    } catch (e) {
      console.warn("LocalStorage cleanup failed:", e);
    }
    setIsReady(true);
  }, []);

  const get = useCallback(<T,>(key: string): T | null => {
    try {
      const raw = localStorage.getItem(CACHE_PREFIX + key);
      if (!raw) return null;
      const entry: CacheEntry<T> = JSON.parse(raw);
      return entry.data;
    } catch {
      return null;
    }
  }, []);

  const set = useCallback(<T,>(key: string, data: T) => {
    try {
      const entry: CacheEntry<T> = {
        data,
        timestamp: Date.now(),
      };
      localStorage.setItem(CACHE_PREFIX + key, JSON.stringify(entry));
    } catch (e) {
      // LocalStorage might be full or disabled
      console.warn("Failed to cache data:", e);
    }
  }, []);

  const clear = useCallback((key?: string) => {
    try {
      if (key) {
        localStorage.removeItem(CACHE_PREFIX + key);
      } else {
        // Clear all cache entries
        const keys = getCacheKeys();
        keys.forEach((k) => localStorage.removeItem(CACHE_PREFIX + k));
      }
    } catch (e) {
      console.warn("Failed to clear cache:", e);
    }
  }, []);

  const remove = useCallback((key: string) => {
    try {
      localStorage.removeItem(CACHE_PREFIX + key);
    } catch (e) {
      console.warn("Failed to remove cache key:", e);
    }
  }, []);

  const isStale = useCallback(
    (key: string, ttl: number = DEFAULT_TTL): boolean => {
      try {
        const raw = localStorage.getItem(CACHE_PREFIX + key);
        if (!raw) return true;
        const entry = JSON.parse(raw);
        return Date.now() - entry.timestamp > ttl;
      } catch {
        return true;
      }
    },
    [],
  );

  // Don't render children until cache cleanup is done
  if (!isReady) return null;

  return (
    <CacheContext.Provider value={{ get, set, clear, remove, isStale }}>
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
