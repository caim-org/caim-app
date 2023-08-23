
# Caim app


### Static and media

These are all hosted on an S3 bucket. Configured with the `MEDIA_USE_S3` env var.

### Image CDN / resizing

We wanted to use an external image resize service in order to avoid load on the main server (hence we rejected sorl-thumnail etc). 

We use imagekit.io for the image transforms. However because imagekit has limited free bandwidth, we put amazon cloudfront in front of it. Thus repeat images should be served by cloudfront for very cheap bandwidth, but transforms are processed by imagekit.

Imagekit is configured to use the media S3 bucket as an origin. Ask Al for imagekit login.

We have a macro that converts the django media URL to the correct imagekit + cloudfront one. 

```
<img src="{{ image.photo.url|image_resize:'800x500 max' }}" />
```

This is configured by 2 settings:
- IMAGE_RESIZE_ORIGIN - The django media root (the photo storage S3 bucket hostname) to be replaced
- IMAGE_RESIZE_CDN - The root of the AWS cloudfront distribution in front of imagekit

### Avatars

User avatars are powered by https://django-avatar.readthedocs.io/en/stable/

### Comments

Each Animal record can have many AnimalComments. Each comment belongs to a user. Comments are plaintext, and processed with `urlizetrunc` and `linebreaks`.

Comments can be edited and deleted. A comment can be edited or deleted by the comment author or a staff user.

In the future we might want to add extra logic here, e.g. a comment can be edited for X minutes by the author. Also we might want nested comments.

### Shortlist

A user can shortlist many animals. Powered by a simple API to set and upset the shortlist status for a given animal.

### Frontend

The app is rendered as Django templates.

We use good old jQuery for js. 

Slideshow is https://github.com/sachinchoolur/lightslider. Just copied the dist folder into static for ease.


## Local development

First, you'll need to install the gdal and pango libraries. For Mac OS, this is as easy as `brew install pango gdal`.

Running the app locally requires:

1. The correct env variables via `source local.env`
2. Making a virtual env `mkvirtualenv caim-django` and then `pip install -r requirements.txt`
3. Running the postgres container via `docker compose up`
4. Migrate the database via `python manage.py migrate`
5. Build test data with `python manage.py shell < seed.py`

Notes:
- The postgres local docker image listenes on port 5434 (rather than the default postgres port of 5432) to avoid clashes if you happen to have postgres running locally on your machine

## How to contribute

We welcome your help! Please browse the attached project and issues for things to work on (more will be added shortly). Please branch off `main`, implement your feature, and send a pull request.

## Hosting

The app is currently hostest on AWS AppRunner. 

### Deployment notes

To deploy to the staging site:

```
1) Login to AWS ECR (need AWS access and correct AWS_PROFILE):

AWS_PROFILE=caim aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 324366619902.dkr.ecr.us-east-1.amazonaws.com

2) Build image and push to staging ECR
docker buildx build --platform linux/amd64 -t 324366619902.dkr.ecr.us-east-1.amazonaws.com/caim-app-staging:latest --push .

3) Build image and push to prod ECR
docker buildx build --platform linux/amd64 -t 324366619902.dkr.ecr.us-east-1.amazonaws.com/caim-app-prod:latest --push .
```
