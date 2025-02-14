import { FormLogin, Root } from "./components";


export function PageLogin(props: {
  loginErr: string
}) {
  return (
    <Root>
      <FormLogin />
    </Root>
  )
}