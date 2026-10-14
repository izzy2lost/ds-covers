# ds-covers

Nintendo DS box art and game titles for [NinDS](https://github.com/izzy2lost), downloaded by the app on demand.

| Path | What it is |
| --- | --- |
| `covers/<GAMEID>.webp` | Box art, 480×432, one per game ID (the 4-character code in the ROM header at 0x0C, e.g. `AMCE` for Mario Kart DS USA) |
| `index.txt` | Every game ID that has a cover, one per line |
| `titles/<LANG>.txt` | GameTDB title lists, `GAMEID = Title`, for EN DE ES FR IT JA KO NL PT RU ZHCN ZHTW |
| `database/dstdb.zip` | The full GameTDB DS database (XML) |

The app fetches files from `https://raw.githubusercontent.com/izzy2lost/ds-covers/main/`. It reads `index.txt` first, so when a game's own region has no cover it borrows the same game's cover from another region.

## Rebuilding

```sh
python3 -I tools/build.py ~/Downloads/DS_Covers ~/Desktop/GameTDB_DS/database
```

This reads the region packs (`DS_covers_<REGION>.zip`), keeps one cover per game ID, preferring the pack that matches the ID's region letter, and re-encodes each cover as WebP at quality 90. Covers that already exist are skipped, so delete `covers/` to rebuild from scratch.

## Credits

Box art and the database come from [GameTDB](https://www.gametdb.com), upscaled 2×.
