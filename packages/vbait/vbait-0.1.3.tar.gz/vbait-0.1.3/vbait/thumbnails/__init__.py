"""
test url
http://127.0.0.1:8000/thumbnails/storeimages/company/iphone5s-selection-summary-2013.png?wid=100&hei=100&fmt=jpeg&qlt=80&cache=1

urls.py
url(r'^thumbnails/', include('packages.thumbnails.urls')),

/thumbnails/storeimages/ - url for view
company/iphone5s-selection-summary-2013.png - path to file

storage - default_storage (MEDIA_ROOT) or custom, for Generator class



GET params:

wid - width thumb
hei - height thumb
fmt - format thumb, png or jpeg
qlt - quality thumb (only jpeg)
cache - 1 or 0, 0 - save in file system, 1 - write in stream
fill - 1 or 0, 0 - no fill content
cover - 1, resize to cover rect
crop - 1, 1 - crop image, then cover = 1
"""