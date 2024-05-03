# README

## Run and Dev mode

Fill .env file:
````
TRINITY_WEB_DEV_DATABASE_USERNAME=<your_postgres_username>
TRINITY_WEB_DEV_DATABASE_PASSWORD=<your_postgres_password>
````

Install dependencies:
```bash
bundle install
npm install
```
Run front dev build:
```bash 
foreman start -f Procfile.dev
```

Run server development local:
```bash
bundle exec rails s -b 127.0.0.1 -p 8080
```
Run server development:
```bash
bundle exec rails s -b 192.168.1.55 -p 8080      
```
Run server production:
```bash
bundle exec rails s -e production -b 192.168.1.55 -p 8080
```
