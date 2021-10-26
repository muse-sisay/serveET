#  <em>servidora</em>

a telegram bot for automating virtual machine provisioning.

This is part of my **serveEthiopia project**, a project aimed at providing resources for fellow Ethiopians to help them in their IT career. You can 

```
git clone https://github.com/muse-sisay/serveET
```

##  Installation // 

<em>servidora</em> is tested to work on `Python 3.9` and above. The required python packages are listed in [requirements.txt](requirements.txt). To install those packages run 
```console
python3 -m pip install -r requirements.txt
```
Depending on your machine you might have to use python3.9 instead.

For my python projects I always like to have a python virtual environments per project to keep my dependencies separate
```console
python3.9 -m venv ~/venv/<venv_name>
```
You need to activate the virtual environment before using you can use it. If you are using fish shell the file is activate.fish
```console
~/venv/<venv_name>/bin/activate(.fish) # to activate
```

Rename config.yml.sample to config.yml.
```
mv src/config.yml.sample to src/config.yml
```

## Up and Running 
### Getting API token for your bot

Start a conversation with [Bot Father](https://t.me/BotFather). Follow through the process of creating a bot. Then save you API token in a safe place, preferably in `src/config.yml`.

### Setting up Proxmox Credentials

Select _Data Center_ in your proxmox server and create a new user. Give the user an appropriate name that describes its function. After that go ahead and create an API token for the user you just created. Copy the  secret key to `src/config.yml`

Create a **Role** with the following privileges.
```text
VM.Audit, VM.Monitor, Datastore.AllocateSpace, VM.Clone, VM.Allocate, VM.PowerMgm
```

Under permission tab click `API Token Permission` and add `/vms` and `/storage` entries.
```
path [/vms | /storage]
API Token  <one you created>
Role <the one you created>
```

### Run bot
```console
python3 src/main.py
```