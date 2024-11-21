# trenchview

Tools for viewing the trenches. 

![](trenchview-demo.gif)

## install

1. Install [pipx](https://github.com/pypa/pipx).
2. `pipx install trenchview`

### setup telethon

You need to take a couple steps to bot your tg account so that it can read your chats programmatically. 

Follow the setup [here](https://docs.telethon.dev/en/stable/basic/signing-in.html#signing-in).

Then, set the following env vars based on the values you generated there:
`TG_API_ID`
`TG_API_HASH`

## usage

### tg-recent-calls

Check recent calls in a tg group. Curretly scoped to The Lab.

`trenchview recent-calls --help`