// src/components/SpaceExplorer.tsx
'use client';

import React, { useState, useEffect } from 'react';
import { Card } from '../components/ui/card';
import { Alert } from '../components/ui/alert';
import { generateStars, getPlanetStyle } from '../lib/utils';
import { planets } from '../config/planets-config';
import Planet from './Planet';

const SpaceExplorer = () => {
  const [currentLevel, setCurrentLevel] = useState(1);
  const [discoveredPlanets, setDiscoveredPlanets] = useState<Set<string>>(new Set());
  const [playingSound, setPlayingSound] = useState(false);
  const [showVictory, setShowVictory] = useState(false);
  const stars = generateStars(50);

  // Audio context setup
  const [audioContext] = useState(() => new (window.AudioContext || (window as any).webkitAudioContext)());

  // Play sound when planet is discovered
  const playPlanetSound = async (note: string) => {
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

    oscillator.frequency.value = noteToFreq[note];
    gainNode.gain.value = 0.1;

    oscillator.start();
    await new Promise(resolve => setTimeout(resolve, 500));
    oscillator.stop();
  };

  const handlePlanetClick = async (planet: typeof planets[0]) => {
    if (discoveredPlanets.has(planet.id) || playingSound) return;

    setPlayingSound(true);
    await playPlanetSound(planet.sound);
    setPlayingSound(false);

    const newDiscovered = new Set(discoveredPlanets);
    newDiscovered.add(planet.id);
    setDiscoveredPlanets(newDiscovered);

    // Show fact about the planet
    Alert({
      title: planet.name,
      description: planet.fact,
      variant: 'default'
    });

    // Check if level is complete
    if (newDiscovered.size === planets.length) {
      setShowVictory(true);
      // Play victory melody
      for (const p of planets) {
        await playPlanetSound(p.sound);
      }
    }
  };

  return (
    <Card className="w-full max-w-4xl p-6">
      <div className="text-2xl font-bold mb-4">
        Milky Way Explorer - Level {currentLevel}
      </div>

      <div className="relative h-96 bg-slate-900 rounded-lg overflow-hidden">
        {/* Twinkling stars background */}
        <div className="absolute inset-0">
          {stars.map((star, i) => (
            <div
              key={i}
              className="absolute w-px h-px bg-white rounded-full animate-twinkle"
              style={{
                left: `${star.left}%`,
                top: `${star.top}%`,
                animationDelay: `${star.delay}s`
              }}
            />
          ))}
        </div>

        {/* Space glow effect */}
        <div className="absolute inset-0 bg-gradient-radial from-blue-500/5 via-transparent to-transparent" />

        {/* Planets */}
        {planets.map(planet => (
          <Planet
            key={planet.id}
            {...planet}
            discovered={discoveredPlanets.has(planet.id)}
            onClick={() => handlePlanetClick(planet)}
          />
        ))}

        {/* Victory effect */}
        {showVictory && (
          <div className="absolute inset-0 bg-white/10 animate-pulse duration-1000">
            <div className="flex items-center justify-center h-full">
              <div className="text-white text-3xl font-bold">
                Level Complete! 🎉
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="mt-4 text-sm text-gray-500">
        Click on planets to discover facts about our solar system!
      </div>
    </Card>
  );
};

export default SpaceExplorer;