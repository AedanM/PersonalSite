# Personal Website

Initially designed to serve as a repo for me to store movies I want to watch, this has bloomed into a full website. Built with the awesome [uv Package Manger](https://github.com/astral-sh/uv) and Django running on Python 3.13.
Currently hosted on [aedanm.uk](https://aedanm.uk)

## Features

### Media Database

Catalogue of films that interest me. Built on a SQLite DB, which I can update while on the go to make sure I remember any films/tv/etc that I want to watch. Statsistics on watch length, decade trends, etc are generated for general interest.
[Link to site](https://aedanm.uk/media)

### Media Database FastAPI

To make some automated testing and data entry easier, I added a FastAPI side to the website to quickly access data and update fields.
[Link to site](https://aedanm.uk/media/api)

### Static Blog

Mostly unused besides personal notes, there is a static blog host for any musings/thoughts I have.
[Link to site](https://aedanm.uk/blog)

### Resume Hosting

I also use the awesome `json-resume` to generate my resume template as both html and pdf and host it as part of the website
[Link to site](https://aedanm.uk/resume)

