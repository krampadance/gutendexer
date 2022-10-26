# Gutendexer

The api that collects data from [gutendex api](http://gutendex.com) and also offers the chance to add reviews on several books.

It is base on the description found in Software Engineer Challenge pdf.

# Technologies used
To develop the api, [Fastapi web framework](https://fastapi.tiangolo.com/) was used.

For storing data, [MongoDB](https://www.mongodb.com/) was selected.

For building Docker was chosen.

# Installation
I wanted to try out [Poetry](https://python-poetry.org), so, you can see lots of poetry related files.

In order to install Poetry you can follow this link: [poetry-installation](https://python-poetry.org/docs/#installation).

If you use poetry, you can install the dependencies by running:

`poetry install`

Apart from that I also extracted the requirements.txt file, so you can use normal python flow to install dependencies.

First create and activate a python virtual environment:

`python3 -m venv /path/to/new/virtual/environment`

then activate it:

`source /path/to/new/virtual/environment/bin/activate`

and install dependencies withL

`pip3 install -r requirements.txt`

# Run
Before running the app, we need to start the database

`docker-compose up mongodb`

Then you can either use:

`poetry run uvicorn gutendexer.main:app --reload`

or

`uvicorn gutendexer.main:app --reload`

to start the api locally.

Alternatively, you can use the whole docker-compose file to have everything setup.

`docker-compose up`

Once up, you can connect to the api through the browser

`http://localhost:8000`

`http://localhost:8000/docs/`, to get the openapi documentation of the api and also be able to use the endpoints of it.

# Tests
To run the tests, you need to run them locally. So have the mongodb instance running, and run

`pytest`

in the command shell.

The tests should connect to the test database and not mess up with main database of the project.

# Thought process
The thought process can be found in the thoughtProcess.pdf file.

# Development process
You can also check the development process on the several branches used and pull requests made.

