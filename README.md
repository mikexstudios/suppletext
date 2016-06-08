suppletext
==========

**This is no longer developed with last commits in 2009.**

<img src="https://github.com/mikexstudios/suppletext/blob/master/static/base/images/combined_screenshot_884x278.png">

suppleText is a very flexible and elegant wiki focused on semantics, clean aesthetics, web standards, usability, permissions, and giving users the power to customize the presentation of the wiki.

It was developed with the intention of being an open source project with an accompanying SaaS service for wiki hosting. Users can sign up in just two clicks (logging in with social accounts that they already own) to receive a wiki at `yourname.suppletext.com` (and the ability to point any domain to it). Unfortunately, this project ended early when I started graduate school and did not have time to continue working on it.

## Screenshots

<table>
<tr>
  <td align="center" width="33%">
   <img src="https://github.com/mikexstudios/suppletext/blob/master/screenshots/home.png" width="100%">
   <p><strong>Home 1</strong></p>
  </td>
  <td align="center" width="33%">
    <img src="https://github.com/mikexstudios/suppletext/blob/master/screenshots/home2.png" width="100%">
    <p><strong>Home 2</strong></p>
  </td>
  <td align="center" width="33%">
    <img src="https://github.com/mikexstudios/suppletext/blob/master/screenshots/home3.png" width="100%">
    <p><strong>Home 3</strong></p>
  </td>
</tr>
<tr>
  <td align="center">
   <img src="https://github.com/mikexstudios/suppletext/blob/master/screenshots/signup1.png" width="100%">
   <p><strong>Sign up by social login</strong></p>
  </td>
  <td align="center">
    <img src="https://github.com/mikexstudios/suppletext/blob/master/screenshots/signup2.png" width="100%">
    <p><strong>Sign up, pick wiki name</strong></p>
  </td>
  <td align="center">
    <img src="https://github.com/mikexstudios/suppletext/blob/master/screenshots/mywiki.png" width="100%">
    <p><strong>My wiki</strong></p>
  </td>
</tr>
<tr>
  <td align="center">
   <img src="https://github.com/mikexstudios/suppletext/blob/master/screenshots/edit.png" width="100%">
   <p><strong>Edit page</strong></p>
  </td>
  <td align="center">
    <img src="https://github.com/mikexstudios/suppletext/blob/master/screenshots/edit2.png" width="100%">
    <p><strong>Edit page 2</strong></p>
  </td>
  <td align="center">
    <img src="https://github.com/mikexstudios/suppletext/blob/master/screenshots/edit-quickformat.png" width="100%">
    <p><strong>Quick formatting rules</strong></p>
  </td>
</tr>
<tr>
  <td align="center">
   <img src="https://github.com/mikexstudios/suppletext/blob/master/screenshots/formatting-01.png" width="100%">
   <p><strong>Formatting Rules 1</strong></p>
  </td>
  <td align="center">
    <img src="https://github.com/mikexstudios/suppletext/blob/master/screenshots/formatting-02.png" width="100%">
    <p><strong>Formatting Rules 2</strong></p>
  </td>
  <td align="center">
    <img src="https://github.com/mikexstudios/suppletext/blob/master/screenshots/formatting-03.png" width="100%">
    <p><strong>Formatting Rules 3</strong></p>
  </td>
</tr>
<tr>
  <td align="center">
   <img src="https://github.com/mikexstudios/suppletext/blob/master/screenshots/formatting-04.png" width="100%">
   <p><strong>Formatting Rules 4</strong></p>
  </td>
  <td align="center">
    <img src="https://github.com/mikexstudios/suppletext/blob/master/screenshots/formatting-05.png" width="100%">
    <p><strong>Formatting Rules 5</strong></p>
  </td>
  <td align="center">
    <img src="https://github.com/mikexstudios/suppletext/blob/master/screenshots/formatting-06.png" width="100%">
    <p><strong>Formatting Rules 6</strong></p>
  </td>
</tr>
<tr>
  <td align="center">
   <img src="https://github.com/mikexstudios/suppletext/blob/master/screenshots/preview.png" width="100%">
   <p><strong>Preview Edits</strong></p>
  </td>
  <td align="center">
    <img src="https://github.com/mikexstudios/suppletext/blob/master/screenshots/settings.png" width="100%">
    <p><strong>Settings</strong></p>
  </td>
  <td align="center">
    <img src="https://github.com/mikexstudios/suppletext/blob/master/screenshots/settings-users.png" width="100%">
    <p><strong>Settings - User management</strong></p>
  </td>
</tr>

</table>

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
