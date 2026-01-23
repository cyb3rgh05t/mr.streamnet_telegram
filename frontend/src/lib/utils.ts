import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatUptime(uptime: string): string {
  return uptime;
}

export function formatDate(date: string): string {
  return new Date(date).toLocaleDateString();
}
