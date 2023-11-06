
# Caim app


## Static and media

These are all hosted on an S3 bucket. Configured with the `MEDIA_USE_S3` environment variable (refer to `caim/settings.py` or to `docker-compose.yml` for a set of relevant environment variables).

## App features

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

## Code organization

Application code lives in `caim_base`.

## Frontend

The app is rendered as Django templates.

CSS styling based on the bootstrap framework.

We use a mix of good old jQuery and HTMX for interactivity.

Slideshow is https://github.com/sachinchoolur/lightslider. Just copied the dist folder into static for ease.

## Local development

First, you'll need to install the gdal and pango libraries. For Mac OS, this is as easy as `brew install pango gdal`.

Running the app locally requires:

1. Making a virtual env `mkvirtualenv caim-django` and then `pip install -r requirements.txt`
2. Running the postgres container via `docker compose up`
3. Make migrations for built-in Django model changes via `python manage.py makemigrations`
4. Migrate the database via `python manage.py migrate`
5. Build test data with `python manage.py shell < seed.py`

After you've set up the app, you can start it by running `./run.sh`.

Notes:
- The postgres local docker image listens on port 5434 (rather than the default postgres port of 5432) to avoid clashes if you happen to have postgres running locally on your machine

## Testing

We have a nacent testing Github workflow which will run on pull requests. Most functionality is not covered by automated testing and improved automated tests would be a significant benefit for reliability and velocity.

## How to contribute

We welcome your help! Please browse the attached project and issues for things to work on (more will be added shortly). Please branch off `main`, implement your feature, and send a pull request.

To land commits to the main branch, you must be added to the `@caim-org/engineers` team.

## Hosting

The app is currently hosted on AWS AppRunner. There is a staging environment and a production environment.

The app relies on a number of environment variables which are set within the AWS console for each environment. The environment variables we rely on can be found in `caim/settings.py`. 

### Service dependencies

We're integrated with Salesforce and Supabase (for Postgres hosting). Salesforce can be disabled via setting the `SALESFORCE_ENABLED` environment variable to `0`. Postgres is configured through DB environment variables. A DB is required for the app to function, so hosting must be established.

### Logging

We have some logging enabled for the app but not much is currently being logged. Logging is configured to output to stdout.

### Deployment notes

Deployment is managed by Github Actions. There are two automated workflows, `Deploy to staging` and `Deploy to production`. Both of these workflows operate on commits to the main branch,
which is a source of workflow issues. In the future, it would be useful to move the staging deployment upstream of a commit to the main branch.

#### Deploy to staging

Runs on every commit and deploys the app to AWS App Runner staging environment.

#### Deploy to production

Runs on commits tagged with a semver version (eg, v1.0.0) and deploys the app to AWS App Runner production environment.