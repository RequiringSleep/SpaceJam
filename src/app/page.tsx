'use client';

import React from 'react';

export default function SpaceExplorer() {
  const [currentLevel, setCurrentLevel] = React.useState(1);
  const [discoveredPlanets, setDiscoveredPlanets] = React.useState<Set<string>>(new Set());
  const [playingSound, setPlayingSound] = React.useState(false);
  const [showVictory, setShowVictory] = React.useState(false);

  // Generate stars for the background
  const stars = Array.from({ length: 50 }, (_, i) => ({
    left: Math.sin(i * 3) * 50 + 50,
    top: Math.sin(i * 3 + 1) * 50 + 50,
    delay: Math.sin(i * 3 + 2) * 1.5 + 1.5
  }));

  const planets = [
    {
      id: 'mercury',
      name: 'Mercury',
      size: 'w-12 h-12',
      position: 'top-1/4 left-1/4',
      fact: 'The smallest planet in our solar system!',
      sound: 'C4'
    },
    {
      id: 'venus',
      name: 'Venus',
      size: 'w-16 h-16',
      position: 'top-1/2 left-1/3',
      fact: 'The hottest planet in our solar system!',
      sound: 'E4'
    },
    {
      id: 'earth',
      name: 'Earth',
      size: 'w-16 h-16',
      position: 'bottom-1/3 right-1/3',
      fact: 'The only known planet with life!',
      sound: 'G4'
    },
    {
      id: 'mars',
      name: 'Mars',
      size: 'w-14 h-14',
      position: 'bottom-1/4 right-1/4',
      fact: 'Known as the Red Planet!',
      sound: 'B4'
    }
  ];

  const handlePlanetClick = async (planet: typeof planets[0]) => {
    if (discoveredPlanets.has(planet.id) || playingSound) return;

    setPlayingSound(true);
    try {
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();

      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);

      const noteToFreq: { [key: string]: number } = {
        'C4': 261.63,
        'E4': 329.63,
        'G4': 392.00,
        'B4': 493.88
      };

      oscillator.frequency.value = noteToFreq[planet.sound];
      gainNode.gain.value = 0.1;

      oscillator.start();
      await new Promise(resolve => setTimeout(resolve, 500));
      oscillator.stop();
    } finally {
      setPlayingSound(false);
    }

    const newDiscovered = new Set(discoveredPlanets);
    newDiscovered.add(planet.id);
    setDiscoveredPlanets(newDiscovered);

    if (newDiscovered.size === planets.length) {
      setShowVictory(true);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24 bg-black">
      <div className="w-full max-w-4xl p-6 bg-slate-800 rounded-lg">
        <div className="text-2xl font-bold mb-4 text-white">
          Milky Way Explorer - Level {currentLevel}
        </div>

        <div className="relative h-96 bg-slate-900 rounded-lg overflow-hidden">
          {/* Stars */}
          <div className="absolute inset-0">
            {stars.map((star, i) => (
              <div
                key={i}
                className="absolute w-px h-px bg-white rounded-full animate-pulse"
                style={{
                  left: `${star.left}%`,
                  top: `${star.top}%`,
                  animationDelay: `${star.delay}s`
                }}
              />
            ))}
          </div>

          {/* Planets */}
          {planets.map(planet => (
            <button
              key={planet.id}
              onClick={() => handlePlanetClick(planet)}
              className={`
                absolute rounded-full cursor-pointer 
                transition-all duration-500
                ${planet.size} ${planet.position}
                ${discoveredPlanets.has(planet.id)
                  ? 'ring-4 ring-white shadow-lg animate-pulse' 
                  : 'hover:ring-2 hover:ring-white/50'
                }
                ${planet.id === 'mercury' ? 'bg-orange-400' : ''}
                ${planet.id === 'venus' ? 'bg-yellow-200' : ''}
                ${planet.id === 'earth' ? 'bg-blue-400' : ''}
                ${planet.id === 'mars' ? 'bg-red-500' : ''}
              `}
            />
          ))}

          {/* Victory */}
          {showVictory && (
            <div className="absolute inset-0 bg-white/10 animate-pulse">
              <div className="flex items-center justify-center h-full">
                <div className="text-white text-3xl font-bold">
                  Level Complete! 🎉
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="mt-4 text-sm text-gray-400">
          Click on planets to discover facts about our solar system!
        </div>
      </div>
    </main>
  );
}