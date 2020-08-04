# Dynamic Voice Channels

## Introduction

Have you always wanted a fast discord bot that automatically creates new voice channels and is also easy to use?  Then this bot is perfect for you. It automatically creates a new voice channel as soon as you join a certain channel and deletes it afterwards.

## Examples

- **Dynamic channels:**

![Example](https://i.imgur.com/40zpISm.gif)

- **Easy settings:**

![Example](https://i.imgur.com/R05aMGl.gif)

## Setup

You can change the prefix using **`dvc!prefix <new prefix>`**

**1. Setting the channel:**

You can either use **`dvc!setup`** to setup a new category and a new channel or **`dvc!add <channel>`** to add the initial channel. The channel can be removed later with **`dvc!remove <channel>`**. You can see all set auto-channels using **`dvc!list`**.

**2. Editing the default settings:**

You can change settings using **`dvc!setup`**. The bot will start an interactive session where you can change the name, limit, position and category of new channels.

**3. Blacklist bad words:**

To blacklist certain words in channel names you can use the **`dvc!blacklist <word>`** command. Bad words are replaced with asterisks. To remove the word use **`dvc!whitelist <word>`**.

## Commands:

When creating a new channel you will get the **`manage channel`** permission in this channel. Every user with this permission can use commands to modify the channel.

### Managing:

- **`dvc!name <new name>`** Sets a name
- **`dvc!limit <new limit>`** Sets a limit
- **`dvc!kick <member>`** Kicks someone

### Permissions:

- **`dvc!permit <member>`** Gives someone `manage channel` permission.
- **`dvc!transfer <member>`** Transfers your permission
- **`dvc!claim`** Claims permission after the owner has left the channel

### Connecting:

- **`dvc!close [member|role]`** Denies connecting
- **`dvc!open [member|role]`** Removes connection overwrites
- **`dvc!grant [member|role]`** Allows connecting 

### Visibility:

- **`dvc!hide [member|role]`** Makes your channel hidden
- **`dvc!unhide [member|role]`** Makes your channel no longer hidden
- **`dvc!show [member|role]`** Makes your channel visible

### Other:

- **`dvc!help [command]`** Help!
- **`dvc!invite`** Get the invite
- **`dvc!info`** Bot info


## Links

- [Invite Link](https://discord.com/oauth2/authorize?client_id=723665963123343480&scope=bot&permissions=16796752)
- Support Server (coming soon)
