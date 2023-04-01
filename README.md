# ScrapPages

## API

"/profiles"
* GET: get a list of users
* POST: create a new user
  - requires "username" and "password"

"/profiles/*USERNAME*"
* GET: get a particular user
* PUT: edit a particular user
  - requires authentication
  - can include "display_name" and "description"
  - can include an image "profile_picture" as the new profile picture for the user
* DELETE: delete a particular user
  - requires authentication

"/profiles/*USERNAME*/scraps"
* GET: get a particular user's scraps

"/scraps"
* GET: get a list of scraps
* POST: create a new scrap
  - requires authentication
  - must be written as a multipart request
  - must include "title" and the file itself
  - can include "description"
  - optionally includes a "tags" list
  - file must be of type PNG, JPG, GIF, or TXT

"/scraps/*ID*"
* GET: get a particular scrap
* PUT: edit a scrap
  - requires authentication
  - can include "title" and "description"
* DELETE: deletes a work
  - requires authentication

"/scraps/*ID*/like"
* POST: creates a like
  - requires authentication
* DELETE: deletes a like
  - requires authentication

"/scraps/*ID*/comments"
* GET: get the comments on a particular scrap
* POST: creates a new comment
  - requires authentication
  - must include "content"

"/scraps/*ID*/comments/*CID*"
* GET: get a particular comment on a particular scrap
* POST: creates a new comment as a reply to this one
  - requires authentication
* PUT: edit a comment
  - requires authentication
  - can include "content"
* DELETE: deletes a comment
  - requires authentication

"/scraps/*ID*/comments/*CID*/like"
* POST: creates a like
  - requires authentication
* DELETE: deletes a like
  - requires authentication

"/scraps/*ID*/tags"
* GET: get the list of tags for the particular scrap
* POST: posts a new tag under the scrap
  - requires authentication
  - can include "tag"
* DELETE: deletes an existing tag from the scrap
  - requires authentication
  - requires "tag"

"/scraps/tagged/*TAG*"
* GET: get a list of works with a particular tag
