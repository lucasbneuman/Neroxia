import { NextRequest, NextResponse } from 'next/server';

const MARKETING_HOSTS = new Set(['neroxia.tech', 'www.neroxia.tech']);
const APP_HOST = 'app.neroxia.tech';

const APP_PATHS = ['/dashboard', '/login', '/signup', '/onboarding'];
const MARKETING_PATHS = ['/', '/platform', '/pricing'];

function isAppPath(pathname: string) {
  return APP_PATHS.some((path) => pathname === path || pathname.startsWith(`${path}/`));
}

function isMarketingPath(pathname: string) {
  return MARKETING_PATHS.some((path) => pathname === path || pathname.startsWith(`${path}/`));
}

export function proxy(request: NextRequest) {
  const host = request.headers.get('host')?.split(':')[0] ?? '';
  const { pathname } = request.nextUrl;

  if (MARKETING_HOSTS.has(host) && isAppPath(pathname)) {
    const url = request.nextUrl.clone();
    url.hostname = APP_HOST;
    return NextResponse.redirect(url);
  }

  if (host === APP_HOST && pathname === '/') {
    const url = request.nextUrl.clone();
    url.pathname = '/login';
    return NextResponse.redirect(url);
  }

  if (host === APP_HOST && isMarketingPath(pathname)) {
    const url = request.nextUrl.clone();
    url.hostname = 'neroxia.tech';
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
