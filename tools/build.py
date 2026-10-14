#!/usr/bin/env python3
"""Builds this repo's covers/ and titles/ from the source packs.

  python3 -I tools/build.py ~/Downloads/DS_Covers ~/Desktop/GameTDB_DS/database

Covers: every DS_*_<REGION>.zip of <GAMEID>.webp. A game ID can appear in
several region packs; the pack matching the ID's region letter wins, then EN,
US, JP and the rest. Each cover is re-encoded as lossy WebP (quality 90) to
keep the repo small. index.txt lists every game ID that has a cover, so the
app can look up a fallback region instead of probing for 404s.

Titles: GameTDB's dstdb-<LANG>.txt ("ID = Title") copied as titles/<LANG>.txt.
"""
import io
import multiprocessing
import os
import re
import shutil
import sys
import zipfile

from PIL import Image

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUALITY = 90
# The fourth character of a game ID is its region.
NATIVE = {"E": "US", "J": "JP", "P": "EN", "D": "DE", "F": "FR", "I": "IT", "S": "ES",
          "H": "NL", "K": "KO", "U": "AU", "C": "CH", "R": "RU", "Q": "DK", "N": "NO",
          "Z": "SE", "V": "EN", "X": "EN", "Y": "EN"}
FALLBACK = ["EN", "US", "JP", "DE", "FR", "ES", "IT", "NL", "AU", "KO", "SE", "DK", "NO", "FI", "PT", "RU", "CH"]


def encode(job):
    zpath, name, dst = job
    if os.path.isfile(dst):
        return
    with zipfile.ZipFile(zpath) as z:
        im = Image.open(io.BytesIO(z.read(name)))
        im.load()
    tmp = dst + ".tmp"
    im.save(tmp, "WEBP", quality=QUALITY, method=6)
    os.replace(tmp, dst)


def main(covers_dir, db_dir):
    packs = {}
    for f in os.listdir(covers_dir):
        m = re.match(r"DS_\w+?_([A-Z]{2})\.zip$", f)
        if m:
            packs[m.group(1)] = os.path.join(covers_dir, f)
    have = {}  # id -> {region: member name}
    for region, path in packs.items():
        with zipfile.ZipFile(path) as z:
            for n in z.namelist():
                m = re.fullmatch(r"([A-Z0-9]{4})\.webp", os.path.basename(n))
                if m:
                    have.setdefault(m.group(1), {})[region] = n
    jobs = []
    os.makedirs(os.path.join(OUT, "covers"), exist_ok=True)
    for gid, regions in sorted(have.items()):
        order = [NATIVE.get(gid[3])] + FALLBACK + sorted(regions)
        region = next(r for r in order if r in regions)
        jobs.append((packs[region], regions[region], os.path.join(OUT, "covers", gid + ".webp")))
    with multiprocessing.Pool() as pool:
        for i, _ in enumerate(pool.imap_unordered(encode, jobs, chunksize=16), 1):
            if i % 500 == 0 or i == len(jobs):
                print(f"covers {i}/{len(jobs)}", flush=True)
    with open(os.path.join(OUT, "index.txt"), "w") as f:
        f.write("".join(gid + "\n" for gid in sorted(have)))
    os.makedirs(os.path.join(OUT, "titles"), exist_ok=True)
    for f in sorted(os.listdir(db_dir)):
        m = re.fullmatch(r"dstdb-(\w+)\.txt", f)
        if m:
            shutil.copyfile(os.path.join(db_dir, f), os.path.join(OUT, "titles", m.group(1) + ".txt"))
    os.makedirs(os.path.join(OUT, "database"), exist_ok=True)
    shutil.copyfile(os.path.join(db_dir, "dstdb.zip"), os.path.join(OUT, "database", "dstdb.zip"))
    print("done", flush=True)


if __name__ == "__main__":
    main(*sys.argv[1:3])
