#!/usr/bin/env python
import gdata.photos.service
import argparse

parser = argparse.ArgumentParser(
    description='Delete all photos in Google+/Picasa.')
parser.add_argument('-u', '--username',
                    help='Your googlemail username (e.g. bob or '
                         'bob@yourdomain.com)')
parser.add_argument('-p', '--password',
                    help='Your googlemail password. If you use 2-factor '
                         'authentication then get a per-app password')
args = parser.parse_args()

# Create a client class which will make HTTP requests with Google Docs server.
client = gdata.photos.service.PhotosService()
# Authenticate using your Google Docs email address and password.
client.ClientLogin(args.username, args.password)

oldcount = -1
count = 0
failedpics = []
while True:
    print
    print "Doing another GET"
    if oldcount == count:
        print "No more photos that can be deleted are being returned by the query."
        break
    oldcount = count
    for album in client.GetUserFeed().entry:
        print "Album id: " + album.gphoto_id.text
        print "Number of photos: " + album.numphotos.text
        try:
            client.Delete(album.GetEditLink().href)
        except:
            print "Could not delete album; deleting all photos inside, instead"
            for photo in client.GetFeed('/data/feed/api/user/args.username/albumid/%s?kind=photo' % (album.gphoto_id.text)).entry:
                print
                print "Photo ID: " + photo.gphoto_id.text
                if photo.gphoto_id.text not in failedpics:
                    print "Size: " + photo.width.text + "x" + photo.height.text
                    print "      " + photo.size.text + " bytes"
                    print photo.GetHtmlLink().href
                    print photo.GetMediaURL()
                    try:
                        client.Delete(photo)
                    except:
                        print "DELETE PHOTO FAILED " + photo.gphoto_id.text
                        failedpics.append(photo.gphoto_id.text)
                        continue
                    count += 1
                    print "Deleted %d Photos" % count

print
print("Finished. Or maybe got stuck due to the following photos that I "
      "can't delete. Sometimes trying again after a while helps!")
for i in failedpics:
    print "* " + i
