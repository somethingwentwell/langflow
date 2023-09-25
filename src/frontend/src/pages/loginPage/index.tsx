import * as Form from "@radix-ui/react-form";
import { useContext, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import InputComponent from "../../components/inputComponent";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { CODE_PROMPT_DIALOG_SUBTITLE, CONTROL_LOGIN_STATE } from "../../constants/constants";
import { alertContext } from "../../contexts/alertContext";
import { AuthContext } from "../../contexts/authContext";
import { getLoggedUser, onLogin } from "../../controllers/API";
import { LoginType } from "../../types/api";
import {
  inputHandlerEventType,
  loginInputStateType,
} from "../../types/components";
import { BASE_URL_API } from "../../constants/constants";
import { useEffect } from "react"; // Add this import 

export default function LoginPage(): JSX.Element {
  const [inputState, setInputState] =
    useState<loginInputStateType>(CONTROL_LOGIN_STATE);

  const { password, username } = inputState;
  const { login, getAuthentication, setUserData, setIsAdmin } =
    useContext(AuthContext);
  const navigate = useNavigate();
  const { setErrorData } = useContext(alertContext);

  const redirectUri = window.location.href.toString();
  const login_url = `${BASE_URL_API}oauth2?call_type=login`;

  function handleInput({
    target: { name, value },
  }: inputHandlerEventType): void {
    setInputState((prev) => ({ ...prev, [name]: value }));
  }

  function signIn() {
    const user: LoginType = {
      username: username.trim(),
      password: password.trim(),
    };
    onLogin(user)
      .then((user) => {
        login(user.access_token, user.refresh_token);
        getUser();
        navigate("/");
      })
      .catch((error) => {
        setErrorData({
          title: "Error signing in",
          list: [error["response"]["data"]["detail"]],
        });
      });
  }

  function oauth2SignIn() {
    window.location.href = login_url;
  }

  function getUser() {
    if (getAuthentication()) {
      setTimeout(() => {
        getLoggedUser()
          .then((user) => {
            const isSuperUser = user!.is_superuser;
            setIsAdmin(isSuperUser);
            setUserData(user);
          })
          .catch((error) => {});
      }, 500);
    }
  }

  useEffect(() => {  
    async function fetchData() {
      const urlParams = new URLSearchParams(window.location.search);  
      const code = urlParams.get("code");  
      const state = urlParams.get("state");
    
      if (code && state) {  
        // let user = await handleOauth2Callback(code, state);  
        let token_response = await fetch(`${BASE_URL_API}oauth2_callback?code=${code}&state=${state}`);
        let token = await token_response.json();
        let user_tokens_res = await fetch(`${BASE_URL_API}oauth2_get_user_token?access_token=${token.access_token}&id_token=${token.id_token}`);
        let user = await user_tokens_res.json();
        login(user.access_token, user.refresh_token);
        getUser();
        navigate("/");
      }  
    }
    fetchData();

  }, []);  

  return (
    <Form.Root
      onSubmit={(event) => {
        if (password === "") {
          event.preventDefault();
          return;
        }
        signIn();
        const data = Object.fromEntries(new FormData(event.currentTarget));
        event.preventDefault();
      }}
      className="h-full w-full"
    >
      <div className="flex h-full w-full flex-col items-center justify-center bg-muted">
        <div className="flex w-72 flex-col items-center justify-center gap-2">
          <span className="mb-4 text-5xl">⛓️</span>
          <span className="mb-6 text-2xl font-semibold text-primary">
            Sign in to Langflow
          </span>
          <div className="mb-3 w-full">
            <Form.Field name="username">
              <Form.Label className="data-[invalid]:label-invalid">
                Username <span className="font-medium text-destructive">*</span>
              </Form.Label>

              <Form.Control asChild>
                <Input
                  type="username"
                  onChange={({ target: { value } }) => {
                    handleInput({ target: { name: "username", value } });
                  }}
                  value={username}
                  className="w-full"
                  required
                  placeholder="Username"
                />
              </Form.Control>

              <Form.Message match="valueMissing" className="field-invalid">
                Please enter your username
              </Form.Message>
            </Form.Field>
          </div>
          <div className="mb-3 w-full">
            <Form.Field name="password">
              <Form.Label className="data-[invalid]:label-invalid">
                Password <span className="font-medium text-destructive">*</span>
              </Form.Label>

              <InputComponent
                onChange={(value) => {
                  handleInput({ target: { name: "password", value } });
                }}
                value={password}
                isForm
                password={true}
                required
                placeholder="Password"
                className="w-full"
              />

              <Form.Message className="field-invalid" match="valueMissing">
                Please enter your password
              </Form.Message>
            </Form.Field>
          </div>
          <div className="w-full">
            <Form.Submit asChild>
              <Button className="mr-3 mt-6 w-full" type="submit">
                Sign in
              </Button>
            </Form.Submit>
          </div>
          <div className="w-full">
            <Button className="w-full bg-info-content" onClick={oauth2SignIn}>
              OAuth 2.0 Sign In
            </Button>
          </div>
          <div className="w-full">
            <Link to="/signup">
              <Button className="w-full" variant="outline" type="button">
                Don't have an account?&nbsp;<b>Sign Up</b>
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </Form.Root>
  );
}
