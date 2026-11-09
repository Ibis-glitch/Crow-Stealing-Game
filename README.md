# The Crow Job: Pygame Starter

A small top-down stealth-and-looting prototype. The graphics are placeholder shapes so you can replace them with your own pixel art.

## Run it

1. Install Python 3.
2. Open this folder in VS Code.
3. Open the integrated terminal.
4. Install Pygame:

   ```bash
   python -m pip install -r requirements.txt
   ```

5. Run:

   ```bash
   python main.py
   ```

On some systems, use `python3` instead of `python`.

## Controls

- **WASD / Arrow keys:** Move
- **Shift:** Sprint (faster, but you can tune the noise/detection behavior)
- **E:** Pick up a nearby object
- **Space:** Hide or emerge when next to a marked hiding spot
- **Enter:** Escape through the green exit when carrying at least one item
- **Esc:** Quit
- **R:** Restart after being caught or winning

## Where to add your art

The game currently draws simple placeholder rectangles and shapes. Suggested assets:

- `assets/sprites/crow.png`
- `assets/sprites/resident.png`
- `assets/sprites/items/`
- `assets/tiles/house_tileset.png`

The internal game resolution is **320 x 180**, scaled up by 4 using nearest-neighbor scaling. This keeps the pixel edges crisp. Make sprites with transparent backgrounds and use small dimensions, such as 8x8, 16x16, or 24x24.

## Suggested next steps

1. Replace `Crow.draw`, `Resident.draw`, and `Treasure.draw` in `entities.py` with sprite blits.
2. Replace `House.draw` with your tilemap or room artwork.
3. Add sound effects for footsteps, item pickup, and detection.
4. Improve resident AI with room-to-room patrol routes and line-of-sight checks.
5. Add a title screen and a nest/collection screen.

## Current prototype limitations

- Residents use a simple proximity detection radius, not directional vision or wall occlusion.
- The room layout is a placeholder made from rectangles.
- The three houses are defined in `house.py`; adjust them there.
- The inventory has a fixed capacity of three objects.
