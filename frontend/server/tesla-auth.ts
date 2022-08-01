import * as crypto from 'crypto';
import {URL, URLSearchParams} from 'url';

import fetch from 'node-fetch';
import * as cheerio from 'cheerio';
import * as urlbase64 from 'url-safe-base64';
import * as cookie from 'cookie';
import * as setcookie from 'set-cookie-parser';

export async function authenticateWithTesla(username: string, password: string, token: string): Promise<string> {
	const loginPage = await getLoginPage(username);
  const loginResponse = await sendLoginRequest(loginPage, username, password);

  return JSON.stringify(loginResponse);
}


const stableState = 'a long stable random string';
const userAgent = 'hoff-tesla-client';

function parseLoginPage(body: string, cookieHeader: string) {
	const $ = cheerio.load(body);

	const hiddenInputAttribs = $('input[type="hidden"]').toArray().map(input => input.attribs);
	const hiddenValues = hiddenInputAttribs.reduce((accum, next) => {
		return {
			...accum,
			[next.name]: next.value,
		};
	}, {} as Record<string, string>);

	return {
		cookie: cookieHeader.split(' ')[0],
		hiddenValues,
	};
}

interface loginPage {
	hiddenValues: Record<string, string>;
	cookie: string;
	codeVerifier: string;
	codeChallenge: string;
	referer: string;
}

async function getLoginPage(email: string): Promise<loginPage> {
	const codeVerifier = urlbase64.encode(crypto.randomBytes(32).toString('base64'));
	const codeChallenge = urlbase64.encode(crypto.createHash('sha256').update(codeVerifier).digest('base64'));

  const url = new URL('https://auth.tesla.com/oauth2/v3/authorize');
  [
    ['client_id', 'ownerapi'],
    ['code_challenge', codeChallenge],
    ['code_challenge_method', 'S256'],
    ['redirect_uri', 'https://auth.tesla.com/void/callback'],
    ['response_type', 'code'],
    ['scope', 'openid email offline_access'],
    ['login_hint', email],
    ['state', stableState],
  ].forEach(pair => url.searchParams.set(pair[0], pair[1]));

  const resp = await fetch(url.href, {
    headers: {
      'User-Agent': userAgent,
    },
  });
  const bodyHtml = await resp.text();

  return {
    ...parseLoginPage(bodyHtml, resp.headers.get('set-cookie') ?? ''),
    codeChallenge,
    codeVerifier,
    referer: url.toString(),
  }
}

async function sendLoginRequest(loginPage: loginPage, username: string, password: string) {
  const url = new URL('https://auth.tesla.com/oauth2/v3/authorize');
  [
    ['client_id', 'ownerapi'],
    ['code_challenge', loginPage.codeChallenge],
    ['code_challenge_method', 'S256'],
    ['redirect_uri', 'https://auth.tesla.com/void/callback'],
    ['response_type', 'code'],
    ['scope', 'openid email offline_access'],
    ['state', stableState],
  ].forEach(pair => url.searchParams.set(pair[0], pair[1]));

  const formData: [string, string][] = Object.entries(loginPage.hiddenValues);
	formData.push(['identity', username]);
	formData.push(['credential', password]);

  const postBody = new URLSearchParams();
  formData.forEach(([key, val]) => {
    postBody.set(key, val);
  });

  const resp = await fetch(url.href, {
    method: 'POST',
    headers: {
      authority: 'auth.tesla.com',
      origin: 'https://auth.tesla.com',
      referer: loginPage.referer,
      'content-type': 'application/x-www-form-urlencoded',
      cookie: loginPage.cookie,
    },
    body: postBody.toString(),
  });

  if (resp.status > 399) {
    throw new Error(`tesla error: status=${resp.status} body=${await resp.text()}`);
  }

  return resp.text();
}

// function getAuthCode(email: string, password: string, mfaCode: string | undefined, loginForm: loginPage): Promise<string> {
// 	const url = new URL('https://auth.tesla.com/oauth2/v3/authorize');
// 	[
// 		['client_id', 'ownerapi'],
// 		['code_challenge', loginForm.codeChallenge],
// 		['code_challenge_method', 'S256'],
// 		['redirect_uri', 'https://auth.tesla.com/void/callback'],
// 		['response_type', 'code'],
// 		['scope', 'openid email offline_access'],
// 		['state', stableState],
// 	].forEach(pair => url.searchParams.set(pair[0], pair[1]));

// 	const formData: [string, string][] = Object.entries(loginForm.hiddenValues);
// 	formData.push(['identity', email]);
// 	formData.push(['credential', password]);

// 	return new Promise<string>((resolve, reject) => {
// 		const request = http.request(url, {

// 			method: 'POST',
// 			headers: {
// 				'content-type': 'application/x-www-form-urlencoded',
// 				'cookie': loginForm.cookie,
// 				'host': 'auth.tesla.com',
// 				'origin': 'https://auth.tesla.com',
// 				'referer': loginForm.referer,
// 			},
// 		}, response => {
// 			let body = '';
// 			response.on('data', d => {
// 				body += d;
// 			});
// 			response.once('end', () => {
// 				if (response.statusCode! > 399) {
// 					response.resume();
// 					reject(`response code ${response.statusCode} in getAuthCode, body: ${body}`);

// 					return;
// 				}

// 				if (/passcode/.test(body)) {
// 					if (typeof mfaCode !== 'string') {
// 						reject('MFA code required');
// 					}
// 				} else {
// 					resolve(response.headers.location ?? '');
// 				}
// 			});
// 			response.once('error', e => reject(e));
// 		});

// 		const postBody = new URLSearchParams();
// 		formData.forEach(([key, val]) => {
// 			postBody.set(key, val);
// 		});

// 		request.once('error', e => reject(e));
// 		request.write(postBody.toString());
// 		request.end();
// 	})
// }

// async function getAuthUrl(email: string) {
// 	const codeVerifier = urlbase64.encode(crypto.randomBytes(32).toString('base64'));
// 	const codeChallenge = urlbase64.encode(crypto.createHash('sha256').update(codeVerifier).digest('base64'));

// 	const data = await new Promise<string>((resolve, reject) => {
// 		const url = new URL('https://auth.tesla.com/oauth2/v3/authorize');
// 		[
// 			['client_id', 'ownerapi'],
// 			['code_challenge', codeChallenge],
// 			['code_challenge_method', 'S256'],
// 			['login_hint', email],
// 			['state', stableState],
// 		].forEach(pair => url.searchParams.set(pair[0], pair[1]));

// 		const req = http.get(url, response => {
// 			if (response.statusCode! > 299) {
// 				response.resume();
// 				reject(`response code ${response.statusCode} in getAuthUrl`);

// 				return;
// 			}

// 			let body = '';
// 			response.on('data', d => {
// 				body += d;
// 			});
// 			response.once('end', () => {
// 				resolve(body);
// 			});
// 			response.once('error', e => reject(e));
// 		});

// 		req.once('error', e => console.error(e));
// 		req.end();
// 	});

// 	return data;
// }

// (async function() {
// 	// const loginPage = await getLoginPage('timandchrisct@gmail.com');
// 	// console.log(JSON.stringify(loginPage, undefined, 2));

// 	// const authLocation = await getAuthCode('timandchrisct@gmail.com', 'CNNg&^KPn0rgGU8Bk83*', undefined, loginPage);
// 	// console.log(`LOCATION: ${authLocation}`);

// 	// console.log(await getAuthUrl('timandchrisct@gmail.com'));

// 	const codeVerifier = urlbase64.encode(crypto.randomBytes(32).toString('base64'));
// 	const codeChallenge = urlbase64.encode(crypto.createHash('sha256').update(codeVerifier).digest('base64'));
// 	const url = new URL('https://auth.tesla.com/oauth2/v3/authorize');
// 		[
// 			['client_id', 'ownerapi'],
// 			['code_challenge', codeChallenge],
// 			['code_challenge_method', 'S256'],
// 			['redirect_uri', 'https://auth.tesla.com/void/callback'],
// 			['response_type', 'code'],
// 			['scope', 'openid email offline_access'],
// 			['login_hint', 'timandchrisct@gmail.com'],
// 			['state', stableState],
// 		].forEach(pair => url.searchParams.set(pair[0], pair[1]));

// 	console.log(url.toString());
// })()
