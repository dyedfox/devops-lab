# Playlist Generator

Creates M3U playlists from audio files in a directory.

## Usage

```bash
./generate-pl.sh [filename] [directory]
```

- `filename` - playlist name (default: "playlist")
- `directory` - folder to search (default: current directory)

## Examples

```bash
# Create playlist.m3u from current directory
./generate-pl.sh

# Create mymusic.m3u from /home/user/Music
./generate-pl.sh mymusic /home/user/Music
```

Supports: MP3, OGG, M4A, FLAC, WAV, AAC, WMA