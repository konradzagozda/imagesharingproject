# Backend (Django) Developer - Images - recruitment task for hexocean

## Quickstart

1. type `docker-compose up` 
2. on 127.0.0.1:8000 application should be running.

## Fixtures

- 3 tiers:
  - basic
  - premium
  - enterprise

- 4 accounts:
  - admin/admin
  - basic/basic - with basic tier
  - premium/premium - user with premium tier
  - enterprise/enterprise - user with enterprise tier

## API overview

- `POST /api/images/` - upload image
- `GET /api/images/`  lists your uploaded images with links available to current tier + temporary links if they were set up.
- `GET /api/images/<uuid>` downloads original-sized image if it's available 
- `GET /api/images/<uuid>/?height=<height>` downloads thumbnail with certain height if available
- `GET /api/images/<uuid>/get_temp_link/?ttl=300&height=300` - creates and returns temporary link for thumbnail if height is present otherwise link for original-sized image is created. ttl has to be put between 300 and 30_000 seconds.
- `GET /api/images/temp/?uuid=<uuid>` - temporary link for downloading image (original or thumbnail)


## Explanations

1. Unauthorized users can download images.
2. Authorized users can upload images.
3. Only admins can create tiers and assign them to users through admin panel.


### Performance considerations

1. Thumbnails are computed only once at first request then stored in filesystem for future use.
2. For future improvements we could use IMDB like redis or memcached.
