import discord
from discord.ext import commands
import datetime
import asyncio
import os

# ================= CONFIG ORIGINAL =================
TOKEN = os.getenv("TOKEN2")
LOG_CHANNEL_ID = 1484326544871526450

ALLOWED_ROLES = [1482423776158154953, 1482425821460304144, 1481089914522173520]
BYPASS_ROLE = 1482423776158154953

BAD_WORDS = ["fdp", "prr", "vtmnc", "caralho", "carai", "puta", "filha da puta", "porra", "vai tomar no cu", "cu", "pinto", "rola"]

# ================= CONFIG NOVA =================
PUNISH_LOG_CHANNEL = 1482500867696627813

ADMIN_ROLES = [1481089914522173520, 1482425821460304144]
STAFF_ROLES = [1482425697736589604]
NOVICE_ROLES = [1483601026820079678]

warns = {}
spam_control = {}

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ================= PERMISSÕES =================
def is_admin(member):
    return any(role.id in ADMIN_ROLES for role in member.roles)

def is_staff(member):
    return any(role.id in STAFF_ROLES for role in member.roles)

def is_novice(member):
    return any(role.id in NOVICE_ROLES for role in member.roles)

def can_punish(member):
    return is_admin(member) or is_staff(member)

def can_warn(member):
    return is_admin(member) or is_staff(member) or is_novice(member)

# ================= LOG ORIGINAL =================
async def send_log(guild, member, reason, duration_min):
    channel = bot.get_channel(LOG_CHANNEL_ID) or await bot.fetch_channel(LOG_CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title="🚨 Punishment Log",
            color=discord.Color.red(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.add_field(name="`Punished user:`", value=f"{member.mention} ({member.id})", inline=False)
        embed.add_field(name="`Motive:`", value=reason, inline=False)
        embed.add_field(name="`Time:`", value=f"{duration_min} minutos", inline=False)
        embed.set_footer(text="Drakion Auto Mod © | All Rights Reserved.", icon_url="https://cdn.discordapp.com/icons/1481089628374171651/de6d926a6fd65da6b783a0f96e929b49.png?size=2048") 
        embed.set_image(url="https://cdn.discordapp.com/attachments/1482181421341872259/1482192202976202783/output.png") 
        embed.set_thumbnail(url="https://cdn.discordapp.com/icons/1481089628374171651/de6d926a6fd65da6b783a0f96e929b49.png?size=2048")

        await channel.send(embed=embed)

# ================= LOG NOVO =================
async def send_punish_log(ctx, user, tipo, motive):
    channel = bot.get_channel(PUNISH_LOG_CHANNEL)

    embed = discord.Embed(
        title="🚨 manual punishment",
        color=discord.Color.red(),
        timestamp=datetime.datetime.utcnow()
    )

    embed.add_field(name="`User:`", value=f"{user.mention} ({user.id})", inline=False)
    embed.add_field(name="`Type:`", value=tipo, inline=False)
    embed.add_field(name="`Staff:`", value=ctx.author.mention, inline=False)
    embed.add_field(name="`Motive:`", value=motive or "Not informed", inline=False)
    embed.set_footer(text="Drakion Auto Mod © | All Rights Reserved.", icon_url="https://cdn.discordapp.com/icons/1481089628374171651/de6d926a6fd65da6b783a0f96e929b49.png?size=2048") 
    embed.set_image(url="https://cdn.discordapp.com/attachments/1482181421341872259/1482192202976202783/output.png") 
    embed.set_thumbnail(url="https://cdn.discordapp.com/icons/1481089628374171651/de6d926a6fd65da6b783a0f96e929b49.png?size=2048")

    await channel.send(embed=embed)

# ================= DM =================
async def send_dm(user, tipo, motive, tempo=None):
    embed = discord.Embed(title="⚠️ You have been punished", color=discord.Color.orange())
    embed.add_field(name="`Type:`", value=tipo, inline=False)
    embed.add_field(name="`Motive:`", value=motive or "Not informed", inline=False)
    embed.set_footer(text="Drakion Auto Mod © | All Rights Reserved.", icon_url="https://cdn.discordapp.com/icons/1481089628374171651/de6d926a6fd65da6b783a0f96e929b49.png?size=2048") 
    embed.set_image(url="https://cdn.discordapp.com/attachments/1482181421341872259/1482192202976202783/output.png") 
    embed.set_thumbnail(url="https://cdn.discordapp.com/icons/1481089628374171651/de6d926a6fd65da6b783a0f96e929b49.png?size=2048")

    if tempo:
        embed.add_field(name="Duração", value=tempo, inline=False)

    try:
        await user.send(embed=embed)
    except:
        pass

# ================= EVENTO =================
@bot.event
async def on_ready():
    print(f'✅ Bot connected as {bot.user}')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # 🔥 BYPASS (SEU SISTEMA)
    if message.author.get_role(BYPASS_ROLE):
        await bot.process_commands(message)
        return

    content_lower = message.content.lower()

    # ================= LINK =================
    if "discord.gg/" in content_lower or "discord.com/invite/" in content_lower:
        user_roles = [role.id for role in message.author.roles]
        if not any(role_id in user_roles for role_id in ALLOWED_ROLES):
            await message.delete()
            return

    # ================= PALAVRÃO =================
    if any(word in content_lower for word in BAD_WORDS):
        await message.delete()
        duration = datetime.timedelta(minutes=1)
        await message.author.timeout(duration)
        await send_log(message.guild, message.author, "swear word", 1)
        return

    # ================= SPAM =================
    user_id = message.author.id
    content_strip = message.content.strip().lower()

    if user_id not in spam_control:
        spam_control[user_id] = [content_strip, 1]
    else:
        if spam_control[user_id][0] == content_strip:
            spam_control[user_id][1] += 1
        else:
            spam_control[user_id] = [content_strip, 1]

    if spam_control[user_id][1] >= 5:
        duration = datetime.timedelta(minutes=5)
        await message.author.timeout(duration)
        await send_log(message.guild, message.author, "Spam", 5)
        spam_control[user_id] = ["", 0]

    await bot.process_commands(message)
    
# ================= PARSER MOTIVE + TEMPO =================
def parse_motive_tempo(texto, tempo_padrao=5):
    partes = texto.split()

    if len(partes) > 1 and partes[-1].isdigit():
        tempo = int(partes[-1])
        motive = " ".join(partes[:-1])
    else:
        tempo = tempo_padrao
        motive = texto

    return motive, tempo
# ================= FUNÇÃO SUCESSO =================
async def send_success(ctx, msg_text):
    embed = discord.Embed(
        description=f"✅ {msg_text}",
        color=discord.Color.green()
    )
    msg = await ctx.send(embed=embed)
    await asyncio.sleep(5)
    await msg.delete()


# ================= ERROS =================
@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.CheckFailure):
        embed = discord.Embed(
            description="❌ You do not have permission to use this command.",
            color=discord.Color.red()
        )

    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            description=f"❌ There's a missing argument: `{error.param.name}`",
            color=discord.Color.red()
        )

    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(
            description="❌ Invalid user or incorrect argument.",
            color=discord.Color.red()
        )

    elif isinstance(error, commands.CommandNotFound):
        return

    else:
        embed = discord.Embed(
            description="❌ An error occurred while executing the command.",
            color=discord.Color.red()
        )
        print(error)

    msg = await ctx.send(embed=embed)
    await asyncio.sleep(5)
    await msg.delete()


# ================= COMANDOS =================

@bot.command()
async def warn(ctx, member: discord.Member, *, motive):
    if not can_warn(ctx.author):
        raise commands.CheckFailure()

    warns[member.id] = warns.get(member.id, 0) + 1

    await send_punish_log(ctx, member, f"Warn ({warns[member.id]}/3)", motive)
    await send_dm(member, "Warning", motive)

    await send_success(ctx, f"Warn aplicado em {member.mention}.")

    if warns[member.id] >= 3:
        await member.timeout(datetime.timedelta(hours=2))
        await send_punish_log(ctx, member, "Auto Mute (2h)", "3 warns")
        await send_dm(member, "Muted", "3 warns", "2 hours")

        await send_success(ctx, f"{member.mention} It was automatically mutated (3 warns).")

        warns[member.id] = 0


@bot.command()
async def mute(ctx, member: discord.Member, *, motive):
    if not can_warn(ctx.author):
        raise commands.CheckFailure()

    motive, tempo = parse_motive_tempo(motive)

    if not motive:
        raise commands.MissingRequiredArgument(ctx.command.params['texto'])

    await member.timeout(datetime.timedelta(minutes=tempo))
    await send_punish_log(ctx, member, f"Mute ({tempo} min)", motive)
    await send_dm(member, "Muted", motive, f"{tempo} minutes")

    await send_success(ctx, f"Mute applied to {member.mention} ({tempo} min). See the log channel.")


@bot.command()
async def kick(ctx, member: discord.Member, *, motive):
    if not can_punish(ctx.author):
        raise commands.CheckFailure()

    await member.kick()
    await send_punish_log(ctx, member, "Kick", motive)

    await send_success(ctx, f"{member.mention} It was successfully kicked.")


@bot.command()
async def ban(ctx, member: discord.Member, *, motive):
    if not can_punish(ctx.author):
        raise commands.CheckFailure()

    await member.ban()
    await send_punish_log(ctx, member, "Ban", motive)

    await send_success(ctx, f"{member.mention} It was successfully banned.")


@bot.command()
async def tempban(ctx, member: discord.Member, *, motive):
    if not can_punish(ctx.author):
        raise commands.CheckFailure()

    motive, tempo = parse_motive_tempo(motive)

    if not motive:
        raise commands.MissingRequiredArgument(ctx.command.params['texto'])

    await member.ban()
    await send_punish_log(ctx, member, f"TempBan ({tempo} min)", motive)

    await send_success(ctx, f"{member.mention} was banned for {tempo} minutes.")

    await asyncio.sleep(tempo * 60)
    await ctx.guild.unban(member)


@bot.command()
async def softban(ctx, member: discord.Member, *, motive):
    if not can_punish(ctx.author):
        raise commands.CheckFailure()

    await member.ban()
    await member.unban()
    await send_punish_log(ctx, member, "SoftBan", motive)

    await send_success(ctx, f"{member.mention} It was successfully softbanned.")


@bot.command()
async def lock(ctx):
    if not can_punish(ctx.author):
        raise commands.CheckFailure()

    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)

    await send_success(ctx, "Channel successfully locked.")


@bot.command()
async def unlock(ctx):
    if not can_punish(ctx.author):
        raise commands.CheckFailure()

    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)

    await send_success(ctx, "Channel unlocked successfully.")
    
bot.run(TOKEN)
