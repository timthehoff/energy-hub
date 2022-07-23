import { FC } from 'react';

import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';

import cryptoRandomString from 'crypto-random-string';
import * as urlbase64 from 'url-safe-base64';

async function digestMessage(message: string) {
  const encoder = new TextEncoder();
  const data = encoder.encode(message);
  const hash = await crypto.subtle.digest('SHA-256', data);

  return urlbase64.encode(btoa(String.fromCharCode(...new Uint8Array(hash))));
}

const stableState = 'this is a stable state string to energy hub';

export const LoginForm: FC = () => {
  const redirect = async () => {
    const codeVerifier = cryptoRandomString({ length: 50, type: 'url-safe' });
    const codeChallenge = await digestMessage(codeVerifier);

    const url = new URL('https://auth.tesla.com/oauth2/v3/authorize');
    [
      ['client_id', 'ownerapi'],
      ['code_challenge', codeChallenge],
      ['code_challenge_method', 'S256'],
      ['redirect_uri', 'https://auth.tesla.com/void/callback'],
      ['response_type', 'code'],
      ['scope', 'openid email offline_access'],
      ['state', stableState],
    ].forEach((pair) => url.searchParams.set(pair[0], pair[1]));

    alert(url.toString());
  };

  return (
    <Box sx={{ width: '100%', maxWidth: 500, margin: '1em' }} flexGrow="1">
      <Typography variant="h5" component="div">
        Click the button to be redirected to Tesla's login form. Once you login
        with your Tesla credentials you will be redirected back here.
      </Typography>
      <Button variant="text" onClick={redirect}>
        Login
      </Button>
    </Box>
  );
};
