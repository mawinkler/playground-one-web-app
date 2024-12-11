# playground-one-web-app

## Setup the Backend Application

```sh
venv
pip install -r requirements.txt 
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

Add a design framework like Material-UI, Tailwind CSS, or Bootstrap for styling:

```sh
npm install @mui/material @emotion/react @emotion/styled
```

## Initial App Setup

`frontend/src/App.jsx`

```jsx
import { useEffect, useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import axios from 'axios';
import { Button } from '@mui/material';

function App() {
  const [count, setCount] = useState(0)
  const [data, setData] = useState(null)

  useEffect(() => {
    axios.get('http://127.0.0.1:5000/api/data')
      .then(response => setData(response.data))
      .catch(error => console.error(error));
  }, []);

  return (
    <>
      <div>
        <a href="https://vite.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React</h1>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
        <p>
          Edit <code>src/App.jsx</code> and save to test HMR
        </p>
      </div>
      <div>
        <h1>React and Flask App</h1>
        <p>{data ? data.message : 'Loading...'}</p>
      </div>
      <div>
        <Button variant="contained" color="primary">Click Me</Button>
      </div>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
    </>
  )
}

export default App
```

## Initial Test

Shell 1:

```sh
python3 backend/app.py
```

Shell 2:

```sh
npm run dev -- --host
```
