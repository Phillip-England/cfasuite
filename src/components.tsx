import { type ReactNode } from "react";

interface RootProps {
  children: ReactNode;
}

export function Root({ children }: RootProps) {
  return (
    <html lang="en">
      <head>
        <meta charSet="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Document</title>
      </head>
      <body>
        {children}
      </body>
    </html>
  );
}

export function FormLogin() {
  return (
    <form method="POST" action='/form/login'>
      <div>
        <label>username</label>
        <input type='text' name='username' defaultValue='admin' />
      </div>
      <div>
        <label>password</label>
        <input type='password' name='password' defaultValue='thepasswordthatbeatsit' />
      </div>
      <input type='submit' />
    </form>
  )
}
