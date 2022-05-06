# Backend (Django) Developer - Images - recruitment task for hexocean


## How to run?


## Explanations

It is not specified who could use the link - I assumed everyone should, so basically we're building a image sharing service.

Users with Enterprise should have an ability to fetch a link that expires a number of seconds - each image upload for 
any of tiers, returns set of links thus for simplification each of those links will have expiry time, technically this 
point is met.

It's good practice to override User model but, it's not necessary here, but tier belongs to user not the other way around.

### Performance considerations

We shouldn't compute thumbnails every time a request is made for it, probably the best idea is to use in-memory-database like redis.
Once computed thumbnail, it should be saved for future use.