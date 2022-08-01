import path from 'path';
import * as url from 'url';

import express from 'express';
import debugHttp from 'debug-http';

import { authenticateWithTesla } from './tesla-auth.js';

const __dirname = url.fileURLToPath(new URL('.', import.meta.url));

if (process.env.NODE_ENVIRONMENT !== 'production') {
  debugHttp();
}

const app = express();
const bytesPerMb = 1000000;

app.use(express.static(path.join(__dirname, '..')));

app.use(express.json({ limit: 10 * bytesPerMb }));

interface loginRequest {
  username: any;
  password: any;
  onetimeToken: any;
}

interface loginResponse {
  authToken?: string;
  error?: string;
}

app.post<'/login', {}, loginResponse, Partial<loginRequest>>('/login', (req, res, next) => {
  return Promise.resolve().then(async () => {
    const {username, password, onetimeToken} = req.body;
    if (!username || !password || !onetimeToken) {
      res.status(400).json({
        error: `Request must include username, password, and onetimeToken`,
      });

      return;
    }

    const authToken = await authenticateWithTesla(username, password, onetimeToken);
    res.status(200).json({
      authToken,
    });
  }).catch(next);
});

app.get('*', (req, res) => {
  res.sendFile('index.html', { root: path.join(__dirname, '..') });
});

app.listen(process.env.PORT || 8080, () => {
  console.log(`server listening on port ${process.env.PORT || 8080}`);
});
