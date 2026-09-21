/// <reference types="vite/client" />

declare module 'tailwind-merge' {
  export function twMerge(...classLists: unknown[]): string;
}
