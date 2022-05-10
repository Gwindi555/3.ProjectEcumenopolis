import asyncio
import discord
from discord.ext import commands
from discord.utils import get
from discord_components import DiscordComponents, Button, ButtonStyle

from data import db_session
from data.users import User
from data.shop import Shop
from data.clan import Clan

from config_1 import settings as config

points = 0
points_lvl_up = 5

client = commands.Bot(command_prefix=config['prefix'], intents=discord.Intents.all())
client.remove_command('help')
sp = []
db_session.global_init("db/db.sqlite")
session = db_session.create_session()

PREFIX = config['prefix']


@client.event
async def on_ready():
    print('Bot connection')
    DiscordComponents(client)
    activity = discord.Game(name="BN: help")
    await client.change_presence(status=discord.Status.online, activity=activity)
    for guild in client.guilds:
        for member in guild.members:
            exists = session.query(User.id).filter_by(name=member.name).first() is not None
            if exists == False:
                users = User(
                    name=member.name,
                    id=member.id,
                    cash=0,
                    rep=0,
                    lvl=1,
                    server_id=guild.id
                )
                session.add(users)
                session.commit()
            else:
                pass


@client.event
async def on_member_join(member):
    exists = session.query(User.id).filter_by(name=member.name).first() is not None
    if exists == False:
        users = User(
            name=member.name,
            id=member.id,
            cash=0,
            rep=0,
            lvl=1,
            server_id=member.guild.id
        )
        session.add(users)
        session.commit()
    else:
        pass


@client.command(pass_context=True)
async def help(ctx):
    embed = discord.Embed(title='Навигация по командам', colour=discord.Color.gold())
    embed.add_field(name='{}balance, cash, баланс, кошелёк'.format(PREFIX),
                    value='Просмотр своего или чужого баланс',
                    inline=False)
    embed.add_field(name='{}award, наградить'.format(PREFIX),
                    value='Прибовляет введённую сумму у пользователя (Администратор)',
                    inline=False)
    embed.add_field(name='{}take, забрать'.format(PREFIX),
                    value='Отнимает введённую сумму у пользователя (Администратор)',
                    inline=False)
    embed.add_field(name='{}add-shop-role, добавить-и-магазин-роль'.format(PREFIX),
                    value='Добавляет роль в магазин (Администратор)',
                    inline=False)
    embed.add_field(name='{}del-shop-role, удалить-роль-из-магазина'.format(PREFIX),
                    value='Удаляет роль в магазин (Администратор)',
                    inline=False)
    embed.add_field(name='{}shop, магазин'.format(PREFIX),
                    value='Показывает магазин',
                    inline=False)
    embed.add_field(name='{}buy, buy-role, купить, купить-роль'.format(PREFIX),
                    value='Вы покупаете роль',
                    inline=False)
    embed.add_field(name='{}+rep, +реп'.format(PREFIX),
                    value='Добавляете репутацию (Администратор)',
                    inline=False)
    embed.add_field(name='{}-rep, -реп'.format(PREFIX),
                    value='Отнимает репутацию (Администратор)',
                    inline=False)
    embed.add_field(name='{}LeaderBord, lb, доска-лидеров'.format(PREFIX),
                    value='Показывает доску лидеров',
                    inline=False)
    embed.add_field(name='{}lvl, лвл'.format(PREFIX),
                    value='Показывает lvl',
                    inline=False)
    embed.add_field(name='{}mute'.format(PREFIX),
                    value='Команда выдаёт роль под названием **MUTE** (Обязательно!), (Администратор).'
                          'Эта команда имеет таймер, записывается так: hour-min-sec',
                    inline=False)
    embed.add_field(name='{}unmute'.format(PREFIX),
                    value='Команда выдаёт забирает под названием **MUTE** (Администратор)',
                    inline=False)
    embed.add_field(name='{}clear, очистить'.format(PREFIX),
                    value='Удаляет введённое кол-во сообщений (Администратор)',
                    inline=False)
    embed.add_field(name='{}clan, клан'.format(PREFIX),
                    value='Команда выводит сообщение с конопками для выбора клана',
                    inline=False)
    embed.add_field(name='{}add-clan, добавить-клан'.format(PREFIX),
                    value='Команда используется для добавления кланнов (роли). Эта команда используется только 3 раза (для создания 3-ёх кланов) (Администратор)',
                    inline=False)
    embed.add_field(name='{}del-clan, удалить-клан'.format(PREFIX),
                    value='Команда используется для удалении кланнов (роли)',
                    inline=False)
    embed.add_field(name='{}help'.format(PREFIX),
                    value='Показывает список команд',
                    inline=False)
    await ctx.send(embed=embed)


@client.command(aliases=['balance', 'cash', 'баланс', 'кошелёк'])
async def __balance(ctx, member: discord.Member = None):
    if member is None:
        user = session.query(User).filter(User.id == ctx.author.id).first()
        await ctx.send(embed=discord.Embed(
            description=f"""Баланс пользователя **{ctx.author.name}** состовляет 
            **{user.cash} :dollar:**"""
        ))
        session.commit()
    else:
        user = session.query(User).filter(User.id == member.id).first()
        await ctx.send(embed=discord.Embed(
            description=f"""Баланс пользователя **{member.name}** состовляет 
            **{user.cash} :dollar:**"""
        ))
        session.commit()


@client.command(aliases=['award', 'наградить'])
@commands.has_permissions(administrator=True)
async def __award(ctx, member: discord.Member = None, amount: int = None):
    if member is None:
        await ctx.send(f"**{ctx.author.name}**, укажите имя пользователя, которому хотите выдать определённую сумму")
    else:
        if amount is None:
            await ctx.send(f"**{ctx.author.name}**, укажите сумму, которую хотите выдать данному пользователю")
        elif amount < 1:
            await ctx.send(f"**{ctx.author.name}**, укажите сумму, больше 1 :dollar:")
        else:
            user = session.query(User).filter(User.id == member.id).first()
            user.cash += amount
            session.commit()
            await ctx.message.add_reaction('✅')


@__award.error
async def role_error(ctx, error):
    if isinstance(error, commands.errors.MissingPermissions):
        await ctx.send(f'**{ctx.author.name}**, у вас недостаточно прав')


@client.command(aliases=['take', 'забрать'])
@commands.has_permissions(administrator=True)
async def __take(ctx, member: discord.Member = None, amount: int = None):
    if member is None:
        await ctx.send(f"**{ctx.author.name}**, укажите имя пользователя, которому хотите забрать определённую сумму")
    else:
        if amount is None:
            await ctx.send(f"**{ctx.author.name}**, укажите сумму, которую хотите забрать у данного пользователя")
        elif amount == 'all':
            user = session.query(User).filter(User.id == member.id).first()
            user.cash -= amount
            session.commit()
            await ctx.message.add_reaction('✅')
        elif amount < 1:
            await ctx.send(f"**{ctx.author.name}**, укажите сумму, больше 1 :dollar:")
        else:
            user = session.query(User).filter(User.id == member.id).first()
            user.cash -= amount
            session.commit()
            await ctx.message.add_reaction('✅')


@__take.error
async def role_error(ctx, error):
    if isinstance(error, commands.errors.MissingPermissions):
        await ctx.send(f'**{ctx.author.name}**, у вас недостаточно прав')


@client.command(aliases=['add-shop-role', 'добавить-и-магазин-роль'])
@commands.has_permissions(administrator=True)
async def __add_shop_role(ctx, role: discord.Role = None, cost: int = None):
    if role is None:
        await ctx.send(f"**{ctx.author.name}**, укажите роль, которую хотите добавить в магазин")
    else:
        if cost is None:
            await ctx.send(f"**{ctx.author.name}**, укажите цену роли, которую хотите добавить в магазин")
        elif cost < 0:
            await ctx.send(f"**{ctx.author.name}**, укажите сумму, больше 0 :dollar:")
        else:
            shop = Shop(
                role_id=role.id,
                id=ctx.guild.id,
                cost=cost
            )
            session.add(shop)
            session.commit()
            await ctx.message.add_reaction('✅')


@__add_shop_role.error
async def role_error(ctx, error):
    if isinstance(error, commands.errors.MissingPermissions):
        await ctx.send(f'**{ctx.author.name}**, у вас недостаточно прав')


@client.command(aliases=['del-shop-role', 'удалить-роль-из-магазина'])
@commands.has_permissions(administrator=True)
async def __del_shop_role(ctx, role: discord.Role = None):
    if role is None:
        await ctx.send(f"**{ctx.author.name}**, укажите роль, которую хотите удалить из магазин")
    else:
        session.query(Shop).filter(Shop.role_id == role.id).delete()
        session.commit()
        await ctx.message.add_reaction('✅')


@__del_shop_role.error
async def role_error(ctx, error):
    if isinstance(error, commands.errors.MissingPermissions):
        await ctx.send(f'**{ctx.author.name}**, у вас недостаточно прав')


@client.command(aliases=['shop', 'магазин'])
async def __shop(ctx):
    embed = discord.Embed(title='Магазин ролей', colour=discord.Color.red())
    # shop = session.query(Shop).filter(Shop.id == ctx.guild.id).first()
    for shop in session.query(Shop).filter(Shop.id == ctx.guild.id).all():
        embed.add_field(
            name=f'Стоимость {shop.cost} :dollar:',
            value=f'Вы приобретаете роль {(ctx.guild.get_role(shop.role_id)).mention}',
            inline=False
        )
    await ctx.send(embed=embed)


@client.command(aliases=['buy', 'buy-role', 'купить', 'купить-роль'])
async def __buy(ctx, role: discord.Role = None):
    shop = session.query(Shop).filter(Shop.role_id == role.id).first()
    user = session.query(User).filter(User.id == ctx.author.id).first()
    if role is None:
        await ctx.send(f"**{ctx.author.name}**, укажите роль, которую хотите приобрести в магазин")
    else:
        if role in ctx.author.roles:
            await ctx.send(f"**{ctx.author.name}**, у вас уже есть данная роль")
        elif shop.cost > user.cash:
            await ctx.send(f"**{ctx.author.name}**, у вас недостаточно средств для покупки роли")
        else:
            await ctx.author.add_roles(role)
            user.cash -= shop.cost
            session.commit()
            await ctx.message.add_reaction('✅')


@client.command(aliases=['+rep', '+реп'])
@commands.has_permissions(administrator=True)
async def __rep(ctx, member: discord.Member = None, amount: int = None):
    user = session.query(User).filter(User.id == member.id).first()
    if member is None:
        await ctx.send(f"**{ctx.author.name}**, укажите участника сервера")
    else:
        if amount is None:
            await ctx.send(f"**{ctx.author.name}**, укажите число, которое прибавится к репутации пользователя")
        elif amount < 0:
            await ctx.send(f"**{ctx.author.name}**, укажите число, больше 0")
        else:
            if member.id == ctx.author.id:
                await ctx.send(f"**{ctx.author.name}**, вы не можете выдавать репутация сами себе")
            else:
                user.rep += amount
                session.commit()
                await ctx.message.add_reaction('✅')


@__rep.error
async def role_error(ctx, error):
    if isinstance(error, commands.errors.MissingPermissions):
        await ctx.send(f'**{ctx.author.name}**, у вас недостаточно прав')


@client.command(aliases=['-rep', '-реп'])
@commands.has_permissions(administrator=True)
async def __rep_(ctx, member: discord.Member = None, amount: int = None):
    user = session.query(User).filter(User.id == member.id).first()
    if member is None:
        await ctx.send(f"**{ctx.author.name}**, укажите участника сервера")
    else:
        if amount is None:
            await ctx.send(f"**{ctx.author.name}**, укажите число, которое прибавится к репутации пользователя")
        elif amount < 0:
            await ctx.send(f"**{ctx.author.name}**, укажите число, больше 0")
        else:
            if member.id == ctx.author.id:
                await ctx.send(f"**{ctx.author.name}**, вы не можете забрать репутацию у самого себе")
            else:
                user.rep -= amount
                session.commit()
                await ctx.message.add_reaction('✅')


@__rep_.error
async def role_error(ctx, error):
    if isinstance(error, commands.errors.MissingPermissions):
        await ctx.send(f'**{ctx.author.name}**, у вас недостаточно прав')


@client.command(aliases=['rep', 'реп', 'my-rep', 'моя-реп'])
async def __my_rep(ctx, member: discord.Member = None):
    if member is None:
        user = session.query(User).filter(User.id == ctx.author.id).first()
        await ctx.send(embed=discord.Embed(
            description=f"Репутация пользователя **{ctx.author.name}** состовляет **{user.rep}** очков"),
            colour=discord.Color.green())
    else:
        user = session.query(User).filter(User.id == member.id).first()
        await ctx.send(embed=discord.Embed(
            description=f"Репутация пользователя **{member.name}** состовляет **{user.rep}** очков"),
            colour=discord.Color.green())


@client.command(aliases=['LeaderBord', 'lb', 'доска-лидеров'])
async def __lb(ctx):
    embed = discord.Embed(title='Топ 10 лучших участников сервера:', colour=discord.Color.random())
    counter = 0
    for user in session.query(User).filter(User.server_id == ctx.guild.id).all():
        if counter <= 10:
            counter += 1
            embed.add_field(
                name=f'# {counter}. {user.name}',
                value=f'Баланс: {user.cash}. LvL: {user.lvl}. Репутация: {user.rep}',
                inline=False
            )
        else:
            pass
    await ctx.send(embed=embed)


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    else:
        await client.process_commands(message)
        global points
        points += 1
    global points_lvl_up
    if points >= points_lvl_up:
        user = session.query(User).filter(User.id == message.author.id).first()
        user.lvl += 1
        session.commit()
        points_lvl_up *= 1.5


@client.command(aliases=['lvl', 'лвл'])
async def __off_lvl(ctx, member: discord.Member = None):
    if member is None:
        user = session.query(User).filter(User.id == ctx.author.id).first()
        await ctx.send(embed=discord.Embed(
            description=f"LVL пользователя **{ctx.author.name}** состовляет **{user.lvl}**"),
            colour=discord.Color.orange())
    else:
        user = session.query(User).filter(User.id == member.id).first()
        await ctx.send(embed=discord.Embed(
            description=f"LVL пользователя **{ctx.author.name}** состовляет **{user.lvl}**"),
            colour=discord.Color.orange())


@client.command(aliases=['clear', 'очистить'])
@commands.has_permissions(administrator=True)
async def __clear(ctx, amount: int = None):
    if amount is None:
        await ctx.send(f"**{ctx.author.name}**, укажите число сообщений, которые вы хотите удалить")
    else:
        await ctx.channel.purge(limit=(amount + 1))


@__clear.error
async def role_error(ctx, error):
    if isinstance(error, commands.errors.MissingPermissions):
        await ctx.send(f'**{ctx.author.name}**, у вас недостаточно прав')


@client.command(aliases=['mute'])
@commands.has_permissions(administrator=True)
async def __mute(ctx, member: discord.Member = None, time_: str = None):
    if member is None:
        await ctx.send(f"**{ctx.author.name}**, укажите участника, которого хотите заглушить")
    else:
        await ctx.channel.purge(limit=1)
        mute_role = discord.utils.get(ctx.message.guild.roles, name='MUTE')
        await member.add_roles(mute_role)
        await ctx.send(f'У {member.name.mention}, ограничени чата, за нарушение прав')
        if time_ is None:
            pass
        else:
            date = time_.split('-')
            hour = int(date[0])
            min = int(date[1])
            sec = int(date[2])
            if int(hour) == 0:
                pass
            else:
                hour *= 3600
            if min == 0:
                pass
            else:
                min *= 60
            dt = hour + min + sec
            for i in range(int(dt), 0, -1):
                await asyncio.sleep(1)
            await member.remove_roles(mute_role)
            await ctx.send(f'{member.mention}, с вас сняты ограничения в чате')


@__mute.error
async def role_error(ctx, error):
    if isinstance(error, commands.errors.MissingPermissions):
        await ctx.send(f'**{ctx.author.name}**, у вас недостаточно прав')


@client.command(aliases=['unmute'])
@commands.has_permissions(administrator=True)
async def __unmute(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send(f"**{ctx.author.name}**, укажите участника, с которого хотите снять ограничение")
    else:
        await ctx.channel.purge(limit=1)
        mute_role = discord.utils.get(ctx.message.guild.roles, name='MUTE')
        await member.remove_roles(mute_role)
        await ctx.send(f'{member.mention}, с вас сняты ограничения в чате')


@__unmute.error
async def role_error(ctx, error):
    if isinstance(error, commands.errors.MissingPermissions):
        await ctx.send(f'**{ctx.author}**, у вас недостаточно прав')


@client.command(aliases=['add-clan', 'добавить-клан'])
@commands.has_permissions(administrator=True)
async def __add_clan(ctx, role: discord.Role = None):
    if role is None:
        await ctx.send(f"**{ctx.author.name}**, укажите роль, которую хотите добавить как название клана")
    else:
        clan = Clan(
            role_id=role.id,
            id=ctx.guild.id,
            role_name=role.name
        )
        session.add(clan)
        session.commit()
        await ctx.message.add_reaction('✅')


@__add_clan.error
async def role_error(ctx, error):
    if isinstance(error, commands.errors.MissingPermissions):
        await ctx.send(f'**{ctx.author.name}**, у вас недостаточно прав')


@client.command(aliases=['del-clan', 'удалить-клан'])
@commands.has_permissions(administrator=True)
async def __del_clan(ctx, role: discord.Role = None):
    if role is None:
        await ctx.send(f"**{ctx.author.name}**, укажите роль, которую хотите удалить как название клана")
    else:
        session.query(Clan).filter(Clan.id == ctx.guild.id, Clan.role_name == role.name).delete()
        session.commit()
        await ctx.message.add_reaction('✅')


@__del_clan.error
async def role_error(ctx, error):
    if isinstance(error, commands.errors.MissingPermissions):
        await ctx.send(f'**{ctx.author.name}**, у вас недостаточно прав')


@client.command(aliases=['clan', 'клан'])
async def __clan(ctx, member: discord.Member = None):
    await ctx.channel.purge(limit=1)
    clan_1 = session.query(Clan).filter(Clan.id == ctx.guild.id).all()[0]
    clan_2 = session.query(Clan).filter(Clan.id == ctx.guild.id).all()[1]
    clan_3 = session.query(Clan).filter(Clan.id == ctx.guild.id).all()[2]
    if member is None:
        await ctx.send(
            embed=discord.Embed(
                title=f'**{ctx.author.name}** В какой клан вы хотите вступить? (Каждый клан закреплён под своим командиром (администратором))',
                colour=discord.Color.blurple()),
            components=[[Button(style=ButtonStyle.red, label=clan_1.role_name),
                         Button(style=ButtonStyle.gray, label=clan_2.role_name),
                         Button(style=ButtonStyle.green, label=clan_3.role_name)
                         ]])
        member = ctx.author
    else:
        await ctx.send(
            embed=discord.Embed(
                title=f'**{member.name}** В какой клан вы хотите вступить? (Каждый клан закреплён под своим командиром (администратором))',
                colour=discord.Color.blurple()),
            components=[[Button(style=ButtonStyle.red, label=clan_1.role_name),
                         Button(style=ButtonStyle.gray, label=clan_2.role_name),
                         Button(style=ButtonStyle.green, label=clan_3.role_name)
                         ]])
    response = await client.wait_for('button_click')
    if response.channel == ctx.channel:
        if response.component.label == clan_1.role_name:
            role = get(ctx.message.guild.roles, name=clan_1.role_name)
            await member.add_roles(role)
            await response.respond(content=f'Отлично! Теперь вы в {clan_1.role_name}')
            await ctx.channel.purge(limit=1)
        elif response.component.label == clan_2.role_name:
            role = get(ctx.message.guild.roles, name=clan_2.role_name)
            await member.add_roles(role)
            await response.respond(content=f'Отлично! Теперь вы в {clan_2.role_name}!')
            await ctx.channel.purge(limit=1)
        elif response.component.label == clan_3.role_name:
            role = get(ctx.message.guild.roles, name=clan_3.role_name)
            await member.add_roles(role)
            await response.respond(content=f'Отлично! Теперь вы в {clan_3.role_name}')
            await ctx.channel.purge(limit=1)


client.run(config['token'])
