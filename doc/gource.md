# Visualizing git repo
## Installation (macOS)
Install gource, ffmpeg
```
brew install gource
brew install ffmpeg
```
## Create video using Gource
Use the parameters as desired.
```
# bigger size
gource -1280x720 -o - | ffmpeg -y -r 60 -f image2pipe -vcodec ppm -i - -vcodec libx264 -preset ultrafast -pix_fmt yuv420p -crf 1 -threads 0 -bf 0 gource.mp4

# smaller size
gource -854x480 --file-idle-time 0 --auto-skip-seconds 1 --seconds-per-day 3 -o - | ffmpeg -y -r 60 -f image2pipe -vcodec ppm -i - -vcodec libx264 -preset ultrafast -pix_fmt yuv420p -crf 1 -threads 0 -bf 0 gource_small.mp4
```
