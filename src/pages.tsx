import { FormLogin, Root, ScoreSelection, StoreSelection } from "./components";

export function PageLogin(props: {
  loginErr: string;
}) {
  return (
    <Root>
      <FormLogin loginErr={props.loginErr} />
    </Root>
  );
}

export function PageScorecard(props: {
  currentPath: string;
}) {
  return (
    <Root>
      <StoreSelection currentPath={props.currentPath} />
      <ScoreSelection />
    </Root>
  );
}
