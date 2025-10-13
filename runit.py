from src.abstract_apis import *
### capture locally
##out = cmd_run("ls -la")  # returns text
##
### capture on remote
##out = cmd_run("ls -la /var/www", user_at_host="solcatcher@23.126.105.154")
##
### sudo capture locally
##out = cmd_run_sudo("apt-get update", key="SUDO_PASSWORD")
##
### sudo capture remote
##out = cmd_run_sudo("systemctl restart nginx", user_at_host="solcatcher@23.126.105.154", key="SUDO_PASSWORD")
##
### legacy file-backed (works as before)
##cmd_run("echo hello", output_text="/tmp/cmd.out", print_output=True)
##cmd_run_sudo("apt-get -y upgrade", user_at_host="...", key="SUDO_PASSWORD", output_text="/tmp/upgrade.out")
##
##input(files)
##
