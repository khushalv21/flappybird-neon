"""Procedural sound effects & synthwave music – zero asset files."""
import math
import struct
import pygame


class SoundEngine:
    def __init__(self):
        self.sr = 44100
        self.music_on = True
        self.sfx_on = True
        self.ok = False
        try:
            self._build_sfx()
            self._build_music()
            self.ok = True
        except Exception:
            pass

    # -- public API --
    def play_flap(self):
        if self.ok and self.sfx_on:
            self.snd_flap.play()

    def play_score(self):
        if self.ok and self.sfx_on:
            self.snd_score.play()

    def play_death(self):
        if self.ok and self.sfx_on:
            self.snd_death.play()

    def play_unlock(self):
        if self.ok and self.sfx_on:
            self.snd_unlock.play()

    def start_music(self):
        if self.ok and self.music_on:
            self.snd_music.play(loops=-1)

    def stop_music(self):
        if self.ok:
            self.snd_music.stop()

    def toggle_music(self):
        self.music_on = not self.music_on
        if self.music_on:
            self.start_music()
        else:
            self.stop_music()

    def toggle_sfx(self):
        self.sfx_on = not self.sfx_on

    # -- generators --
    def _pack(self, samples):
        buf = bytearray()
        for s in samples:
            v = max(-32768, min(32767, int(s)))
            p = struct.pack("<h", v)
            buf.extend(p + p)  # stereo
        return pygame.mixer.Sound(buffer=bytes(buf))

    def _tone(self, freq, dur, vol=0.25, wave="sine"):
        n = int(self.sr * dur)
        out = []
        for i in range(n):
            t = i / self.sr
            if wave == "sine":
                v = math.sin(2 * math.pi * freq * t)
            elif wave == "square":
                v = 1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0
            else:  # saw
                v = 2.0 * (freq * t - math.floor(freq * t + 0.5))
            # envelope
            atk = min(1.0, i / max(1, self.sr * 0.005))
            rel = min(1.0, (n - i) / max(1, self.sr * 0.02))
            out.append(v * vol * 32767 * atk * rel)
        return out

    def _build_sfx(self):
        # Flap: short high blip
        self.snd_flap = self._pack(self._tone(880, 0.06, 0.18))

        # Score: ascending two-note
        s = self._tone(660, 0.06, 0.2) + self._tone(990, 0.08, 0.2)
        self.snd_score = self._pack(s)

        # Death: descending buzz
        n = int(self.sr * 0.35)
        d = []
        for i in range(n):
            t = i / self.sr
            freq = 400 - 280 * (i / n)
            env = (1 - i / n) ** 2
            v = (1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0)
            d.append(v * 0.22 * 32767 * env)
        self.snd_death = self._pack(d)

        # Unlock: triumphant arpeggio C-E-G-C
        u = []
        for f in [523, 659, 784, 1047]:
            u.extend(self._tone(f, 0.09, 0.18))
        self.snd_unlock = self._pack(u)

    def _build_music(self):
        """8-second looping synthwave pad."""
        dur = 8.0
        n = int(self.sr * dur)
        chords = [
            [110, 165, 220],
            [87.3, 130.8, 174.6],
            [130.8, 196, 261.6],
            [98, 147, 196],
        ]
        seg = n // 4
        out = []
        for i in range(n):
            t = i / self.sr
            ci = min(3, i // seg)
            val = 0.0
            for f in chords[ci]:
                val += math.sin(2 * math.pi * f * t)
            val = val / len(chords[ci]) * 0.12
            # LFO
            val *= 0.7 + 0.3 * math.sin(2 * math.pi * 0.4 * t)
            # loop fade
            fade = int(self.sr * 0.15)
            if i < fade:
                val *= i / fade
            elif i > n - fade:
                val *= (n - i) / fade
            out.append(val * 32767)
        snd = self._pack(out)
        snd.set_volume(0.35)
        self.snd_music = snd
