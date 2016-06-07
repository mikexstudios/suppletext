suppletext
==========

suppleText is a very flexible and elegant wiki focused on semantics, clean aesthetics, web standards, usability, permissions, and giving users the power to customize the presentation of the wiki.

It was developed with the intention of being an open source project with an accompanying SaaS service for wiki hosting. Users can sign up in just two clicks (logging in with social accounts that they already own) to receive a wiki at `yourname.suppletext.com` (and the ability to point any domain to it). Unfortunately, this project ended early when I started graduate school and did not have time to continue working on it.

## Usage

1. After cloning this repository, copy `local_settings.py.sample` to 
   `local_settings.py`.

2. Build the `Dockerfile`. Note, this `Dockerfile` uses SQLite and Django's
   development server:

   `docker build -t mikexstudios/suppletext .`

2. Run it like:

   `docker run -d -p 80:80 mikexstudios/suppletext`

   If you want to develop while running the script, mount the current 
   directory by:

   ```docker run -d -p 80:80 -v `pwd`:/usr/src/app mikexstudios/suppletext```

3. Point a base domain to the docker's IP address. For example, edit
   `/etc/hosts` and add:
   
   ```
   192.168.59.103 suppletext.com
   192.168.59.103 mywiki.suppletext.com
   ```

   This is necessary because the code parses subdomains as separate wikis
   so a root domain name is required. You can't access the app by IP 
   address or `localhost`. If you're using boot2docker, get the exposed IP
   of the Docker container with: `boot2docker ip`.

4. Then visit `http://suppletext.com` in your browser. Unfortunately, **social
   logins through Janrain are now broken**. However, you can first login 
   through the administration interface at: `http://suppletext.com/admin` with
   username: `admin` and password: `pass`. Now that you have established a
   login session, you can bypass all of the social logins.
