import { FormLogin, Root } from "./components";

export function PageLogin(props: {
  loginErr: string;
}) {
  return (
    <Root>
      <FormLogin loginErr={props.loginErr} />
    </Root>
  );
}

export function PageScorecard() {
  return (
    <Root>
      <a href='/app/logout'>Logout</a>
    </Root>
  );
}
