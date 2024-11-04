class AudioPlayer {
  private audioContext: AudioContext | null = null;
  private gainNode: GainNode | null = null;
  private volume: number = 50;

  private initializeAudio() {
    if (!this.audioContext) {
      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      this.gainNode = this.audioContext.createGain();
      this.gainNode.connect(this.audioContext.destination);
      this.setVolume(this.volume);
    }
    return this.audioContext;
  }

  setVolume(volume: number) {
    this.volume = volume;
    if (this.gainNode) {
      this.gainNode.gain.value = volume / 100 * 0.1;
    }
  }

  playPlanetSound(note: number) {
    const ctx = this.initializeAudio();
    const oscillator = ctx.createOscillator();
    const noteGain = ctx.createGain();

    oscillator.connect(noteGain);
    noteGain.connect(this.gainNode!);

    oscillator.type = 'sine';
    oscillator.frequency.setValueAtTime(note, ctx.currentTime);

    noteGain.gain.setValueAtTime(0, ctx.currentTime);
    noteGain.gain.linearRampToValueAtTime(1, ctx.currentTime + 0.1);
    noteGain.gain.linearRampToValueAtTime(0, ctx.currentTime + 0.5);

    oscillator.start();
    oscillator.stop(ctx.currentTime + 0.5);

    setTimeout(() => {
      noteGain.disconnect();
      oscillator.disconnect();
    }, 600);
  }

  async playVictoryMelody(notes: number[]) {
    const ctx = this.initializeAudio();

    // Play each note in sequence
    for (let i = 0; i < notes.length; i++) {
      await new Promise<void>(resolve => {
        const oscillator = ctx.createOscillator();
        const noteGain = ctx.createGain();

        oscillator.connect(noteGain);
        noteGain.connect(this.gainNode!);

        oscillator.type = 'sine';
        oscillator.frequency.setValueAtTime(notes[i], ctx.currentTime);

        // Longer notes for victory melody
        noteGain.gain.setValueAtTime(0, ctx.currentTime);
        noteGain.gain.linearRampToValueAtTime(1, ctx.currentTime + 0.1);
        noteGain.gain.linearRampToValueAtTime(0.6, ctx.currentTime + 0.3);
        noteGain.gain.linearRampToValueAtTime(0, ctx.currentTime + 0.6);

        oscillator.start();
        oscillator.stop(ctx.currentTime + 0.6);

        setTimeout(() => {
          noteGain.disconnect();
          oscillator.disconnect();
          resolve();
        }, 300); // Slightly overlap notes for smoother melody
      });
    }
  }
}

export const audioPlayer = new AudioPlayer();