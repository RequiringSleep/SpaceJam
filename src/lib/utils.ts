// src/lib/utils.ts

export function seededRandom(seed: number) {
  const x = Math.sin(seed++) * 10000;
  return x - Math.floor(x);
}

export function generateStars(count: number) {
  return Array.from({ length: count }, (_, i) => ({
    left: seededRandom(i * 3) * 100,
    top: seededRandom(i * 3 + 1) * 100,
    delay: seededRandom(i * 3 + 2) * 3
  }));
}

// Helper function for planet styles
export function getPlanetStyle(name: string): string {
  switch (name.toLowerCase()) {
    case 'mercury':
      return `bg-gradient-to-r from-orange-300 via-yellow-400 to-orange-300 
        after:absolute after:inset-2 after:rounded-full after:border-2 after:border-orange-200/30`;
    case 'venus':
      return `bg-gradient-to-r from-yellow-200 via-orange-200 to-yellow-100 
        after:absolute after:inset-1 after:rounded-full after:border-4 after:border-yellow-100/20`;
    case 'earth':
      return `bg-gradient-to-r from-blue-400 via-green-400 to-blue-500 
        after:absolute after:inset-2 after:rounded-full after:border-2 after:border-blue-200/30`;
    case 'mars':
      return `bg-gradient-to-r from-red-500 via-red-400 to-red-500 
        after:absolute after:inset-2 after:rounded-full after:border-2 after:border-red-300/30`;
    default:
      return 'bg-gray-400';
  }
}