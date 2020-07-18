# Dynamic Voice Channels

## Introduction

Have you always wanted a fast discord bot that automatically creates new voice channels and is also easy to use?  Then this bot is perfect for you. It automatically creates a new voice channel as soon as you join a specified channel and deletes it afterwards.

## Examples

- **Setup the bot:**

![Example](https://i.imgur.com/cMwN3jf.gif)

- **Dynamically create channels:**

![Example](https://i.imgur.com/40zpISm.gif)

## Setup

You can change the prefix using `dvc!prefix <new prefix>`

##### Setting the channel:

Use **`dvc!channel <id or name>`** to set the initial channel.

##### Setting the category (optional):

If you want to, you can specify a category in which new channels should be created in. By default this is the category of the initial channel.

##### Setting the default name for channels (optional):

With **`dvc!defaultname <name> `** you can set a default name for new voice channels. You can also use "@user" to refer to the user who created the channel. E.g. **`dvc!defaultname @user's channel`**

##### Setting the default limit for channels (optional):

As with the name, you can also set the default limit using **`dvc!defaultlimit <limit>`**

##### Setting the position (optional):

Use **`dvc!position`** to change the position of the created voice channels. Channels can either be created below or above the initial channel.
 
## Modifying the voice channel

The bot allows users to easily edit their channels with commands.

### The owner principle

The person who created the channel is considered the "owner" of that channel. The owner has access to many commands to change his channel. After the owner leaves the channel users can claim the ownership by using **`dvc!claim`**. The ownership can also be transfered with **`dvc!transfer <member>`** by the owner.

### Commands:

- `dvc!name <new name>`
- `dvc!limit <new limit>`
- `dvc!lock`
- `dvc!unlock`
- `dvc!hide`
- `dvc!unhide`
- `dvc!kick <member>`
- `dvc!ban <member>`
- `dvc!unban <member>`

## Links

- [Invite Link](https://discord.com/oauth2/authorize?client_id=723665963123343480&scope=bot&permissions=16796752)
- Support Server (coming soon)
