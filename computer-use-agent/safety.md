# Safety Configuration

## Forbidden

Commands blocked unconditionally — the agent will refuse even if the user confirms.

- rm -rf
- dd
- mkfs
- shutdown
- reboot
- halt
- poweroff
- :(){ :|:& };:
- chmod -R 777 /
- chown -R
- > /dev/sda

## Risky

Commands allowed only after explicit user confirmation with a warning.

- rm
- sudo
- git push
- git reset --hard
- git clean
- mv
- chmod
- chown
- kill
- pkill
- curl
- wget
- pip install
- npm install
