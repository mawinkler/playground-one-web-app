# playground-one-web-app

## Setup the Backend Application

```sh
venv
pip install -r backend/requirements.txt 
python3 backend/app.py 
```

## Update NodeJS

```sh
sudo npm install -g n
sudo n lts
npm -version
sudo npm install npm -g
npm -version
npm cache clean --force
```

## Create Frontend

```sh
npm create vite@latest frontend -- --template react
cd frontend
npm install
npm run dev -- --host
```

Install dependencies

- axios: For API requests.
- react-router-dom: For routing (if needed).

```sh
npm install axios react-router-dom
```

Add a design framework like Material-UI, Tailwind CSS, or Bootstrap for styling. Add React Select

```sh
npm install @mui/material @emotion/react @emotion/styled react-select
```

## Initial App Setup

`frontend/src/App.jsx`

## Initial Test

Shell 1:

```sh
python3 backend/app.py
```

Shell 2:

```sh
npm run dev -- --host
```

## Docker

In `frontend/App.jsx` change

```js
  const BASEURL = "http://192.168.1.122:5000"
```

to

```js
  const BASEURL = ""
```

Build

```sh
docker build -t mawinkler/pgoweb . --progress=plain --push --no-cache
```

Run

```sh
docker run \
  -p 5000:5000 \
  -e AWS_ACCESS_KEY_ID=<AWS_ACCESS_KEY_ID> \
  -e AWS_SECRET_ACCESS_KEY=<AWS_SECRET_ACCESS_KEY> \
  mawinkler/pgoweb
```

## Mad Scientist

Link: <https://en.wikipedia.org/wiki/File:Mad_scientist.svg#/media/File:Mad_scientist_transparent_background.svg>