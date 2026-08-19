from discord import Guild


def ban_user(guild: Guild, user_name: str, reason: str):
    member = guild.get_member_named(user_name)
    print(f"Member: {member}")
    if member:
        # member.ban(reason=reason)
        return f"User {user_name} banned successfully."
    else:
        return f"User {user_name} not found."
