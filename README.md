# Backend (Django) Developer - Images - recruitment task for hexocean

## Quickstart



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




## Explanations

1. Unauthorized users can download images.
2. Authorized users can upload images.
3. Only admins can create tiers and assign them to users through admin panel.


### Performance considerations

1. Thumbnails are computed only once at first request then stored in filesystem for future use.
2. For future improvements we could use IMDB like redis or memcached.
