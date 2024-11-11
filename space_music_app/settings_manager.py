def update_volumes(self, master=0.5, music=0.5, effects=0.5):
    """Update volume levels"""
    self.master_volume = master
    self.music_volume = music
    self.effects_volume = effects
    
    # Update current sound volumes
    actual_volume = self.master_volume * self.effects_volume
    pygame.mixer.music.set_volume(self.master_volume * self.music_volume)