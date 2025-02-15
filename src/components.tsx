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

export function FormLogin(props: { loginErr: string }) {
  return (
    <form method="POST" action="/form/login">
      <h1>Login</h1>
      {props.loginErr && <p>{props.loginErr}</p>}
      <div>
        <label>Username</label>
        <input type="text" name="username" defaultValue="admin" />
      </div>
      <div>
        <label>Password</label>
        <input
          type="password"
          name="password"
          defaultValue="thepasswordthatbeatsit"
        />
      </div>
      <input type="submit" />
    </form>
  );
}

export function StoreSelection(props: {
  currentPath: string;
}) {
  return (
    <ul>
      <li>
        <a href={props.currentPath + "?store=southroads"}>Southroads</a>
      </li>
      <li>
        <a href={props.currentPath + "?store=utica"}>Utica</a>
      </li>
    </ul>
  );
}

export function ScoreSelection() {
  return (
    <ul>
      <li>
        <a href="/app/scorecard/leadership">Leadership</a>
      </li>
      <li>
        <a href="/app/scorecard/talent">Talent</a>
      </li>
      <li>
        <a href="/app/scorecard/cem">Customer Experience</a>
      </li>
      <li>
        <a href="/app/scorecard/sales">Sales & Brand Growth</a>
      </li>
      <li>
        <a href="/app/scorecard/finance">Financial Stewardship</a>
      </li>
      <li>
        <a href="/app/logout">Logout</a>
      </li>
    </ul>
  );
}
