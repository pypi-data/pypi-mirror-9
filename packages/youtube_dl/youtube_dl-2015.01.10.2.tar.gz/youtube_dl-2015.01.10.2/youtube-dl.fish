
complete --command youtube-dl --long-option help --short-option h --description 'print this help text and exit'
complete --command youtube-dl --long-option version --description 'print program version and exit'
complete --command youtube-dl --long-option update --short-option U --description 'update this program to latest version. Make sure that you have sufficient permissions (run with sudo if needed)'
complete --command youtube-dl --long-option ignore-errors --short-option i --description 'continue on download errors, for example to skip unavailable videos in a playlist'
complete --command youtube-dl --long-option abort-on-error --description 'Abort downloading of further videos (in the playlist or the command line) if an error occurs'
complete --command youtube-dl --long-option dump-user-agent --description 'display the current browser identification'
complete --command youtube-dl --long-option list-extractors --description 'List all supported extractors and the URLs they would handle'
complete --command youtube-dl --long-option extractor-descriptions --description 'Output descriptions of all supported extractors'
complete --command youtube-dl --long-option default-search --description 'Use this prefix for unqualified URLs. For example "gvsearch2:" downloads two videos from google videos for  youtube-dl "large apple". Use the value "auto" to let youtube-dl guess ("auto_warning" to emit a warning when guessing). "error" just throws an error. The default value "fixup_error" repairs broken URLs, but emits an error if this is not possible instead of searching.'
complete --command youtube-dl --long-option ignore-config --description 'Do not read configuration files. When given in the global configuration file /etc/youtube-dl.conf: Do not read the user configuration in ~/.config/youtube-dl/config (%APPDATA%/youtube-dl/config.txt on Windows)'
complete --command youtube-dl --long-option flat-playlist --description 'Do not extract the videos of a playlist, only list them.'
complete --command youtube-dl --long-option proxy --description 'Use the specified HTTP/HTTPS proxy. Pass in an empty string (--proxy "") for direct connection'
complete --command youtube-dl --long-option socket-timeout --description 'Time to wait before giving up, in seconds'
complete --command youtube-dl --long-option source-address --description 'Client-side IP address to bind to (experimental)'
complete --command youtube-dl --long-option force-ipv4 --short-option 4 --description 'Make all connections via IPv4 (experimental)'
complete --command youtube-dl --long-option force-ipv6 --short-option 6 --description 'Make all connections via IPv6 (experimental)'
complete --command youtube-dl --long-option playlist-start --description 'playlist video to start at (default is %default)'
complete --command youtube-dl --long-option playlist-end --description 'playlist video to end at (default is last)'
complete --command youtube-dl --long-option match-title --description 'download only matching titles (regex or caseless sub-string)'
complete --command youtube-dl --long-option reject-title --description 'skip download for matching titles (regex or caseless sub-string)'
complete --command youtube-dl --long-option max-downloads --description 'Abort after downloading NUMBER files'
complete --command youtube-dl --long-option min-filesize --description 'Do not download any videos smaller than SIZE (e.g. 50k or 44.6m)'
complete --command youtube-dl --long-option max-filesize --description 'Do not download any videos larger than SIZE (e.g. 50k or 44.6m)'
complete --command youtube-dl --long-option date --description 'download only videos uploaded in this date'
complete --command youtube-dl --long-option datebefore --description 'download only videos uploaded on or before this date (i.e. inclusive)'
complete --command youtube-dl --long-option dateafter --description 'download only videos uploaded on or after this date (i.e. inclusive)'
complete --command youtube-dl --long-option min-views --description 'Do not download any videos with less than COUNT views'
complete --command youtube-dl --long-option max-views --description 'Do not download any videos with more than COUNT views'
complete --command youtube-dl --long-option no-playlist --description 'If the URL refers to a video and a playlist, download only the video.'
complete --command youtube-dl --long-option age-limit --description 'download only videos suitable for the given age'
complete --command youtube-dl --long-option download-archive --description 'Download only videos not listed in the archive file. Record the IDs of all downloaded videos in it.' --require-parameter
complete --command youtube-dl --long-option include-ads --description 'Download advertisements as well (experimental)'
complete --command youtube-dl --long-option rate-limit --short-option r --description 'maximum download rate in bytes per second (e.g. 50K or 4.2M)'
complete --command youtube-dl --long-option retries --short-option R --description 'number of retries (default is %default)'
complete --command youtube-dl --long-option buffer-size --description 'size of download buffer (e.g. 1024 or 16K) (default is %default)'
complete --command youtube-dl --long-option no-resize-buffer --description 'do not automatically adjust the buffer size. By default, the buffer size is automatically resized from an initial value of SIZE.'
complete --command youtube-dl --long-option test
complete --command youtube-dl --long-option playlist-reverse --description 'Download playlist videos in reverse order'
complete --command youtube-dl --long-option batch-file --short-option a --description 'file containing URLs to download ('"'"'-'"'"' for stdin)' --require-parameter
complete --command youtube-dl --long-option id --description 'use only video ID in file name'
complete --command youtube-dl --long-option output --short-option o --description 'output filename template. Use %(title)s to get the title, %(uploader)s for the uploader name, %(uploader_id)s for the uploader nickname if different, %(autonumber)s to get an automatically incremented number, %(ext)s for the filename extension, %(format)s for the format description (like "22 - 1280x720" or "HD"), %(format_id)s for the unique id of the format (like Youtube'"'"'s itags: "137"), %(upload_date)s for the upload date (YYYYMMDD), %(extractor)s for the provider (youtube, metacafe, etc), %(id)s for the video id, %(playlist_title)s, %(playlist_id)s, or %(playlist)s (=title if present, ID otherwise) for the playlist the video is in, %(playlist_index)s for the position in the playlist. %(height)s and %(width)s for the width and height of the video format. %(resolution)s for a textual description of the resolution of the video format. %% for a literal percent. Use - to output to stdout. Can also be used to download to a different directory, for example with -o '"'"'/my/downloads/%(uploader)s/%(title)s-%(id)s.%(ext)s'"'"' .'
complete --command youtube-dl --long-option autonumber-size --description 'Specifies the number of digits in %(autonumber)s when it is present in output filename template or --auto-number option is given'
complete --command youtube-dl --long-option restrict-filenames --description 'Restrict filenames to only ASCII characters, and avoid "&" and spaces in filenames'
complete --command youtube-dl --long-option auto-number --short-option A --description '[deprecated; use  -o "%(autonumber)s-%(title)s.%(ext)s" ] number downloaded files starting from 00000'
complete --command youtube-dl --long-option title --short-option t --description '[deprecated] use title in file name (default)'
complete --command youtube-dl --long-option literal --short-option l --description '[deprecated] alias of --title'
complete --command youtube-dl --long-option no-overwrites --short-option w --description 'do not overwrite files'
complete --command youtube-dl --long-option continue --short-option c --description 'force resume of partially downloaded files. By default, youtube-dl will resume downloads if possible.'
complete --command youtube-dl --long-option no-continue --description 'do not resume partially downloaded files (restart from beginning)'
complete --command youtube-dl --long-option no-part --description 'do not use .part files - write directly into output file'
complete --command youtube-dl --long-option no-mtime --description 'do not use the Last-modified header to set the file modification time'
complete --command youtube-dl --long-option write-description --description 'write video description to a .description file'
complete --command youtube-dl --long-option write-info-json --description 'write video metadata to a .info.json file'
complete --command youtube-dl --long-option write-annotations --description 'write video annotations to a .annotation file'
complete --command youtube-dl --long-option write-thumbnail --description 'write thumbnail image to disk'
complete --command youtube-dl --long-option load-info --description 'json file containing the video information (created with the "--write-json" option)' --require-parameter
complete --command youtube-dl --long-option cookies --description 'file to read cookies from and dump cookie jar in' --require-parameter
complete --command youtube-dl --long-option cache-dir --description 'Location in the filesystem where youtube-dl can store some downloaded information permanently. By default $XDG_CACHE_HOME/youtube-dl or ~/.cache/youtube-dl . At the moment, only YouTube player files (for videos with obfuscated signatures) are cached, but that may change.'
complete --command youtube-dl --long-option no-cache-dir --description 'Disable filesystem caching'
complete --command youtube-dl --long-option rm-cache-dir --description 'Delete all filesystem cache files'
complete --command youtube-dl --long-option quiet --short-option q --description 'activates quiet mode'
complete --command youtube-dl --long-option no-warnings --description 'Ignore warnings'
complete --command youtube-dl --long-option simulate --short-option s --description 'do not download the video and do not write anything to disk'
complete --command youtube-dl --long-option skip-download --description 'do not download the video'
complete --command youtube-dl --long-option get-url --short-option g --description 'simulate, quiet but print URL'
complete --command youtube-dl --long-option get-title --short-option e --description 'simulate, quiet but print title'
complete --command youtube-dl --long-option get-id --description 'simulate, quiet but print id'
complete --command youtube-dl --long-option get-thumbnail --description 'simulate, quiet but print thumbnail URL'
complete --command youtube-dl --long-option get-description --description 'simulate, quiet but print video description'
complete --command youtube-dl --long-option get-duration --description 'simulate, quiet but print video length'
complete --command youtube-dl --long-option get-filename --description 'simulate, quiet but print output filename'
complete --command youtube-dl --long-option get-format --description 'simulate, quiet but print output format'
complete --command youtube-dl --long-option dump-json --short-option j --description 'simulate, quiet but print JSON information. See --output for a description of available keys.'
complete --command youtube-dl --long-option dump-single-json --short-option J --description 'simulate, quiet but print JSON information for each command-line argument. If the URL refers to a playlist, dump the whole playlist information in a single line.'
complete --command youtube-dl --long-option print-json --description 'Be quiet and print the video information as JSON (video is still being downloaded).'
complete --command youtube-dl --long-option newline --description 'output progress bar as new lines'
complete --command youtube-dl --long-option no-progress --description 'do not print progress bar'
complete --command youtube-dl --long-option console-title --description 'display progress in console titlebar'
complete --command youtube-dl --long-option verbose --short-option v --description 'print various debugging information'
complete --command youtube-dl --long-option dump-intermediate-pages --description 'print downloaded pages to debug problems (very verbose)'
complete --command youtube-dl --long-option write-pages --description 'Write downloaded intermediary pages to files in the current directory to debug problems'
complete --command youtube-dl --long-option youtube-print-sig-code
complete --command youtube-dl --long-option print-traffic --description 'Display sent and read HTTP traffic'
complete --command youtube-dl --long-option call-home --short-option C --description 'Contact the youtube-dl server for debugging. (Experimental)'
complete --command youtube-dl --long-option encoding --description 'Force the specified encoding (experimental)'
complete --command youtube-dl --long-option no-check-certificate --description 'Suppress HTTPS certificate validation.'
complete --command youtube-dl --long-option prefer-insecure --description 'Use an unencrypted connection to retrieve information about the video. (Currently supported only for YouTube)'
complete --command youtube-dl --long-option user-agent --description 'specify a custom user agent'
complete --command youtube-dl --long-option referer --description 'specify a custom referer, use if the video access is restricted to one domain'
complete --command youtube-dl --long-option add-header --description 'specify a custom HTTP header and its value, separated by a colon '"'"':'"'"'. You can use this option multiple times'
complete --command youtube-dl --long-option bidi-workaround --description 'Work around terminals that lack bidirectional text support. Requires bidiv or fribidi executable in PATH'
complete --command youtube-dl --long-option format --short-option f --description 'video format code, specify the order of preference using slashes, as in -f 22/17/18 .  Instead of format codes, you can select by extension for the extensions aac, m4a, mp3, mp4, ogg, wav, webm. You can also use the special names "best", "bestvideo", "bestaudio", "worst".  By default, youtube-dl will pick the best quality. Use commas to download multiple audio formats, such as -f  136/137/mp4/bestvideo,140/m4a/bestaudio. You can merge the video and audio of two formats into a single file using -f <video-format>+<audio-format> (requires ffmpeg or avconv), for example -f bestvideo+bestaudio.'
complete --command youtube-dl --long-option all-formats --description 'download all available video formats'
complete --command youtube-dl --long-option prefer-free-formats --description 'prefer free video formats unless a specific one is requested'
complete --command youtube-dl --long-option max-quality --description 'highest quality format to download'
complete --command youtube-dl --long-option list-formats --short-option F --description 'list all available formats'
complete --command youtube-dl --long-option youtube-include-dash-manifest
complete --command youtube-dl --long-option youtube-skip-dash-manifest --description 'Do not download the DASH manifest on YouTube videos'
complete --command youtube-dl --long-option merge-output-format --description 'If a merge is required (e.g. bestvideo+bestaudio), output to given container format. One of mkv, mp4, ogg, webm, flv.Ignored if no merge is required'
complete --command youtube-dl --long-option write-sub --description 'write subtitle file'
complete --command youtube-dl --long-option write-auto-sub --description 'write automatic subtitle file (youtube only)'
complete --command youtube-dl --long-option all-subs --description 'downloads all the available subtitles of the video'
complete --command youtube-dl --long-option list-subs --description 'lists all available subtitles for the video'
complete --command youtube-dl --long-option sub-format --description 'subtitle format (default=srt) ([sbv/vtt] youtube only)'
complete --command youtube-dl --long-option sub-lang --description 'languages of the subtitles to download (optional) separated by commas, use IETF language tags like '"'"'en,pt'"'"''
complete --command youtube-dl --long-option username --short-option u --description 'login with this account ID'
complete --command youtube-dl --long-option password --short-option p --description 'account password'
complete --command youtube-dl --long-option twofactor --short-option 2 --description 'two-factor auth code'
complete --command youtube-dl --long-option netrc --short-option n --description 'use .netrc authentication data'
complete --command youtube-dl --long-option video-password --description 'video password (vimeo, smotri)'
complete --command youtube-dl --long-option extract-audio --short-option x --description 'convert video files to audio-only files (requires ffmpeg or avconv and ffprobe or avprobe)'
complete --command youtube-dl --long-option audio-format --description '"best", "aac", "vorbis", "mp3", "m4a", "opus", or "wav"; "%default" by default'
complete --command youtube-dl --long-option audio-quality --description 'ffmpeg/avconv audio quality specification, insert a value between 0 (better) and 9 (worse) for VBR or a specific bitrate like 128K (default %default)'
complete --command youtube-dl --long-option recode-video --description 'Encode the video to another format if necessary (currently supported: mp4|flv|ogg|webm|mkv)' --arguments 'mp4 flv ogg webm mkv' --exclusive
complete --command youtube-dl --long-option keep-video --short-option k --description 'keeps the video file on disk after the post-processing; the video is erased by default'
complete --command youtube-dl --long-option no-post-overwrites --description 'do not overwrite post-processed files; the post-processed files are overwritten by default'
complete --command youtube-dl --long-option embed-subs --description 'embed subtitles in the video (only for mp4 videos)'
complete --command youtube-dl --long-option embed-thumbnail --description 'embed thumbnail in the audio as cover art'
complete --command youtube-dl --long-option add-metadata --description 'write metadata to the video file'
complete --command youtube-dl --long-option xattrs --description 'write metadata to the video file'"'"'s xattrs (using dublin core and xdg standards)'
complete --command youtube-dl --long-option fixup --description '(experimental) Automatically correct known faults of the file. One of never (do nothing), warn (only emit a warning), detect_or_warn(check whether we can do anything about it, warn otherwise'
complete --command youtube-dl --long-option prefer-avconv --description 'Prefer avconv over ffmpeg for running the postprocessors (default)'
complete --command youtube-dl --long-option prefer-ffmpeg --description 'Prefer ffmpeg over avconv for running the postprocessors'
complete --command youtube-dl --long-option exec --description 'Execute a command on the file after downloading, similar to find'"'"'s -exec syntax. Example: --exec '"'"'adb push {} /sdcard/Music/ && rm {}'"'"''


complete --command youtube-dl --arguments ":ytfavorites :ytrecommended :ytsubscriptions :ytwatchlater :ythistory"
