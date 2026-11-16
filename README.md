# Stickman Explainer Studio

Aggressive, vertical (9:16, 1080x1920, 30 fps) 3D-stickman explainer videos, built **from a voiceover MP3 + script** using only code:
three.js (software WebGL in headless Chromium via Playwright) -> JPEG frames piped to ffmpeg -> synthesized SFX/music mixed under the voice.
Reference video: "What happens when you swallow chewing gum" (26.1 s, 784 frames). Style target: Zack D. Films-like (bold expressive 3D characters, constant camera punch-ins, rapid cuts) but code-rendered, not AI video.

## Pipeline (what was actually done)
1. **Timing** (`src/analyze.py`): ffmpeg `silencedetect` (noise -32 dB, min 0.12 s) finds speech segments. Words are distributed inside each segment proportionally to hand-counted syllables, each boundary snapped to the nearest energy valley (+-70 ms) of a 200 Hz RMS envelope. Also writes a per-frame (30 fps) mouth-openness array (RMS / 97th percentile, power 0.8). Output: `assets/timing.json` -> wrapped as `timing.js` (`window.TIMING=...`) because file:// pages can't fetch JSON.
   - Whisper could not be used: model download is blocked by the sandbox network allowlist (HF returns 403). If a transcript with word times is available, use it instead.
2. **Scenes** (`src/index.html`): one three.js scene, one `THREE.Group` per shot, visibility toggled by time. `window.renderFrame(frameIndex)` is deterministic (pure function of time), so frames can be rendered in any order.
3. **Render** (`src/render.js`): Playwright Chromium (`--use-gl=angle --use-angle=swiftshader --enable-unsafe-swiftshader`), viewport 1080x1920, `page.screenshot` JPEG q93 per frame -> ffmpeg stdin (`image2pipe`, libx264 veryfast CRF 18, yuv420p). ~0.3-0.5 s/frame on 2 CPU cores = ~5 min for 26 s.
4. **Sound** (`src/sfx.py`): numpy-synthesized whooshes (scene cuts, 0.28 s before cut), impacts on keyword hits, gulp, splat, pops, rising intestine noise, zap, plus a 140 bpm kick/hat/saw-bass loop. Mixed: `amix` voice 1.0 + fx 0.55, `loudnorm I=-14 TP=-1.5`, AAC 192k. Final mux: `ffmpeg -i silent.mp4 -i mix.m4a -c copy -shortest -movflags +faststart`.
5. **Profile picture** (`src/pfp.js`): reuses the same page, hides scenes, resizes renderer to 1080x1080, yellow sunburst, angry shouting close-up.

## Visual language
- Stickman: white sphere head (r .55), thick black back-face outline hull (scale 1.05), huge eyes with black pupils, angry brow boxes (rotation = side * angry * .55), mouth = flattened black sphere whose height follows the audio envelope, tongue when open > .25. Limbs = outlined cylinders, 2-bone analytic IK (arms l1=l2=.58, legs same) with pole vectors; joints are outlined spheres.
- Backgrounds: canvas **sunburst** textures (alternating rays + halftone dots) on a big plane behind the scene, saturated per scene colour: red (hook), purple (gum), orange/yellow (sarcasm), flesh (stomach), acid green (gum survives), yellow/brown (poop), red (annoyed), navy (calendar), hazard yellow/black (finale).
- Rim lights per scene (`lights:[c1,c2]`) for the cinematic edge glow. Key light + ambient.
- Camera: every scene has a `cam(lt,t)` returning position/look/fov. Global **kick** = sum of exp-decaying impulses at keyword times -> extra shake + FOV -4.5 deg. White **flash** overlay (opacity <= .35) on cuts and hits.
- Cuts every 1-3 s; first shot is a screaming face close-up in the first 0.8 s (hook).
- Captions: HTML overlay, Anton font, 112 px, white with 19 px black stroke (`paint-order: stroke fill`), max 3 words (or 1 long word) per chunk, active word yellow, swear words red, pop-in scale .82->1 with overshoot. **Position: top of frame (top:230px)**, below Shorts' top UI. (Originally 128 px at top:1150px; user asked to move up and shrink slightly.)
- Props are canvas-texture planes: "?!", "RUBBER", "7 YEARS", calendar pages, "STORAGE FACILITY" sign, red X slams (two boxes rotated +-45 deg with outBack scale-in).

## Shot list (times in seconds)
| Time | Shot |
|---|---|
| 0.00-0.81 | "WHAT THE F***": extreme close-up face, red burst, heavy shake, push-in |
| 0.81-3.88 | wide: gum stick to mouth (1.75), gulp bulge travels down torso (2.1-2.9), eyes pop + giant gum ball + "?!" at 3.0, dolly to face at "GUM" |
| 3.88-6.69 | smug low-angle slow clap, point at camera on "dumbass" (5.77) |
| 6.69-10.42 | stomach with face; gum drops down esophagus, impact squash + green splash (7.6); "RUBBER" label at its word; worried shake |
| 10.82-12.97 | food chunks dissolve one by one; angry stomach; orbiting camera |
| 12.97-15.68 | gum ball in sunglasses, aura ring, acid drops bounce off, flex on "survives" (14.245), rolls away |
| 15.68-19.00 | camera rides inside CatmullRom intestine tube (rings, fog, camera point light, fov 60->78) |
| 19.00-19.47 | poop reveal with gum stuck, stink rings, on the word "shit" |
| 19.47-20.30 | "And no,": angry palm-stop close-up |
| 20.30-23.58 | finger-wag + head shake, flying calendar pages, "7 YEARS" pops at "seven", red X slam at "years" (22.5) |
| 23.58-26.13 | angry stomach, sign "STORAGE FACILITY" pops, red X slam at "facility" (25.4), sign falls |

## Lessons / gotchas
- `THREE.CanvasTexture` must set `colorSpace = THREE.SRGBColorSpace` or backgrounds look washed out.
- Vertical frame is narrow: at camera z=8 and fov 40 visible width is only ~3.5 units. Keep titles <= ~3 units wide, pull cameras back (z 8-14) for wide props.
- Pages flying toward the camera hide the character; keep them behind (z<0) and to the sides.
- Mouth/eye geometry must sit on the sphere surface (mouth z=.5, not .47).
- Frames/MP4s are large (25 MB); not committed.
- Use `three@0.160.0` (`build/three.min.js` still exists).

## Usage
```bash
npm i three@0.160.0 @fontsource/anton playwright   # chromium must be installed
cp assets/voiceover.mp3 vo.mp3 && ffmpeg -y -i vo.mp3 -ar 16000 -ac 1 vo.wav
python3 src/analyze.py            # edit the segs list first (times + words + syllables)
python3 -c "import json;print('window.TIMING='+json.dumps(json.load(open('timing.json')))+';')" > timing.js
cp src/index.html src/render.js src/shot.js .   # then edit scenes
node shot.js 0.4 2.0 3.5         # preview stills -> prev_*.jpg
node render.js                   # -> silent.mp4 (set N = frames)
python3 src/sfx.py               # -> fx.wav
ffmpeg -y -i vo.mp3 -i fx.wav -filter_complex "[0:a][1:a]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]" -map "[a]" mix.m4a
ffmpeg -y -i silent.mp4 -i mix.m4a -c copy -shortest -movflags +faststart final.mp4
```
Note: scripts expect to run in the working dir containing `index.html`, `timing.js`, `vo.wav`, `vo.mp3`.
