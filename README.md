# Backend (Django) Developer - Images - recruitment task for hexocean


## How to run?


## Explanations

It is not specified who could use the link - I assumed everyone should, so basically we're building a image sharing service.


### Performance considerations

We shouldn't compute thumbnails every time a request is made for it, probably the best idea is to use in-memory-database like redis.
Once computed thumbnail, it should be saved for future use.