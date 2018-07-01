import discord
from discord.ext import commands

class Events:
    def __init__(self, bot):
        self.bot = bot

    async def on_connect(self):
        """Called when the client has successfully connected to Discord.
        This is not the same as the client being fully prepared, see on_ready() for that.

        The warnings on on_ready() also apply.
        """
        pass

    async def on_ready(self):
        """Called when the client is done preparing the data received from Discord. 
        Usually after login is successful and the Client.guilds and co. are filled up.

        Not guaranteed to be called first, nor once!
        """
        self.bot.app_info = await self.bot.application_info()
        print("-" * 10)
        print(f"Logged in as: {self.bot.user.name}\n"
              f"Using discord.py version: {discord.__version__}\n"
              f"Owner: {self.bot.app_info.owner}\n")
        print("-" * 10)


    async def on_shard_ready(self, shard_id):
        """Similar to on_ready() except used by AutoShardedClient 
        to denote when a particular shard ID has become ready.

        shard_id -- The shard ID that is ready.
        """
        pass

    async def on_resumed(self):
        """Called when the client has resumed a session."""
        pass

    async def on_typing(self, channel, user, when):
        """Called when someone begins typing a message.
        The channel parameter can be a abc.Messageable instance. 
        Which could either be TextChannel, GroupChannel, or DMChannel.
        If the channel is a TextChannel then the user parameter is a Member, otherwise it is a User.

        channel -- The location where the typing originated from.
        user -- The user that started typing.
        when -- A datetime.datetime object representing when typing started.
        """
        pass

    async def on_message(self, message):
        """Called when a Message is created and sent.
        Warning:  Bot's messages and private messages are passed here!

        message -- A Message of the current message.
        """
        pass

    async def on_message_delete(self, message):
        """Called when a message is deleted. 
        If the message is not found in the Client.messages cache, then these events will not be called. 
        This happens if the message is too old or the client is participating in high traffic guilds. 
        To fix this, increase the max_messages option of Client.

        message -- A Message of the deleted message.
        """
        pass

    async def on_message_edit(self, before, after):
        """Called when a Message receives an update event.
        The following non-exhaustive cases trigger this event:

        A message has been pinned or unpinned.
        The message content has been changed.
        The message has received an embed.
                For performance reasons, the embed server does not do this in a “consistent” manner.
        A call message has received an update to its participants or ending time.

        before -- previous version of edited message
        after -- current version of edited message
        """

        pass

    async def on_reaction_add(self, reaction, user):
        """Called when a message has a reaction added to it. 
        Similar to on_message_edit, if the message is not found in the Client.messages cache, 
        then this event will not be called.
        
        reaction -- A Reaction showing the current state of the reaction
        user -- A User or Member of the user who added the reaction
        """
        pass

    async def on_reaction_remove(self, reaction, user):
        """Called when a message has a reaction removed from it. 
        Similar to on_message_edit, 
        if the message is not found in the Client.messages cache, 
        then this event will not be called.

        reaction -- A Reaction showing the current state of the reaction.
        user -- A User or Member of the user who removed the reaction.
        """
        pass

    async def on_reaction_clear(self, message, reactions):
        """Called when a message has all its reactions removed from it. 
        Similar to on_message_edit(), 
        if the message is not found in the Client.messages cache, 
        then this event will not be called.

        message -- The Message that had its reactions cleared.
        reactions -- A list of Reactions that were removed.
        """
        pass

    async def on_private_channel_delete(self, channel):
        """Called whenever a private channel is deleted.

        channel – The abc.PrivateChannel that got deleted.
        """
        pass

    async def on_private_channel_create(self, channel):
        """Called whenever a private channel is created.

        channel – The abc.PrivateChannel that got created.
        """
        pass

    async def on_private_channel_update(self, before, after):
        """Called whenever a private group DM is updated. 
        e.g. changed name or topic.

        before -- The GroupChannel that got updated with the old info.
        after -- The GroupChannel that got updated with the updated info.
        """
        pass

    async def on_guild_channel_delete(self, channel):
        """Called whenever a guild channel is deleted.
        Note that you can get the guild from guild.

        channel -- The abc.GuildChannel that got deleted.
        """
        pass

    async def on_guild_channel_create(self, channel):
        """Called whenever a guild channel is created.
        Note that you can get the guild from guild.

        channel - - The abc.GuildChannel that got created.
        """
        pass

    async def on_guild_channel_update(self, before, after):
        """Called whenever a guild channel is updated. 
        e.g. changed name, topic, permissions.

        before -- The abc.GuildChannel that got updated with the old info.
        after -- The abc.GuildChannel that got updated with the updated info.
        """
        pass

    async def on_guild_channel_pins_update(self, channel, last_pin):
        """Called whenever a message is pinned or unpinned from a guild channel.

        channel -- The abc.GuildChannel that had it’s pins updated.
        last_pin -- A datetime.datetime object representing when the latest 
                    message was pinned or None if there are no pins.
        """
        pass

    async def on_member_join(self, member):
        """Called when a Member joins a Guild.

        member -- The Member that joined.
        """
        pass

    async def on_member_remove(self, member):
        """Called when a Member leaves a Guild.

        member -- The Member that left.
        """
        pass

    async def on_member_update(self, before, after):
        """Called when a Member updates their profile.
        This is called when one or more of the following things change:
            status
            game playing
            avatar
            nickname
            roles
        
        before -- The Member that updated their profile with the old info.
        after -- The Member that updated their profile with the updated info.
        """
        pass

    async def on_guild_join(self, guild):
        """Called when a Guild is either created by the Client or when the Client joins a guild.

        guild -- The Guild that was joined.
        """
        pass

    async def on_guild_remove(self, guild):
        """Called when a Guild is removed from the Client.

        This happens through, but not limited to, these circumstances:
            The client got banned.
            The client got kicked.
            The client left the guild.
            The client or the guild owner deleted the guild.
        In order for this event to be invoked then the Client
        must have been part of the guild to begin with.

        guild -- The Guild that got removed.
        """
        pass

    async def on_guild_update(self, before, after):
        """Called when a Guild updates, 
        for example:
            Changed name
            Changed AFK channel
            Changed AFK timeout
            etc

        before -- The Guild prior to being updated.
        after -- The Guild after being updated.
        """
        pass

    async def on_guild_role_create(self, role):
        """Called when a Guild creates a new Role.
        To get the guild it belongs to, use Role.guild.

        role – The Role that was created.
        """
        pass

    async def on_guild_role_delete(self, role):
        """Called when a Guild deletes a new Role.
        To get the guild it belongs to, use Role.guild.

        role – The Role that was deleted.
        """
        pass

    async def on_guild_role_update(self, before, after):
        """Called when a Role is changed guild-wide.

        before -- The Role that updated with the old info.
        after -- The Role that updated with the updated info.
        """
        pass

    async def on_guild_emojis_update(self, guild, before, after):
        """Called when a Guild adds or removes Emoji.

        guild -- The Guild who got their emojis updated.
        before -- A list of Emoji before the update.
        after -- A list of Emoji after the update.
        """
        pass

    async def on_voice_state_update(self, before, after):
        """Called when a Member changes their VoiceState.
        The following, but not limited to, examples illustrate when this event is called:
            A member joins a voice room.
            A member leaves a voice room.
            A member is muted or deafened by their own accord.
            A member is muted or deafened by a guild administrator.

        member -- The Member whose voice states changed.
        before -- The VoiceState prior to the changes.
        after -- The VoiceState after to the changes.
        """
        pass

    async def on_member_ban(self, guild, user):
        """Called when user gets banned from a Guild.

        guild -- The Guild the user got banned from.
        user -- The user that got banned. Can be either User or Member depending if the
                user was in the guild or not at the time of removal.
        """
        pass

    async def on_member_unban(self, guild, user):
        """Called when a User gets unbanned from a Guild.

        guild -- The Guild the user got unbanned from.
        user -- The User that got unbanned.
        """
        pass

    async def on_group_join(self, channel, user):
        """Called when someone joins a group, 
        i.e. a PrivateChannel with a PrivateChannel.type of ChannelType.group.
        
        channel -- The group that the user joined.
        user -- The user that joined.
        """
        pass

    async def on_group_remove(self, channel, user):
        """Called when someone leaves a group,
        i.e. a PrivateChannel with a PrivateChannel.type of ChannelType.group.

        channel -- The group that the user left.
        user -- The user that left.
        """
        pass

    async def on_relationship_add(self, relationship):
        """Called when a Relationship is added from the ClientUser.

        relationship -- The relationship that was added.
        """
        pass

    async def on_relationship_remove(self, relationship):
        """Called when a Relationship is removed from the ClientUser.

        relationship -- The relationship that was removed.
        """
        pass

    async def on_relationship_update(self, before, after):
        """Called when a Relationship is updated, 
        e.g. when you block a friend or a friendship is accepted.

        before -- The previous relationship status.
        after -- The updated relationship status.
        """
        pass



    # Raw events
    async def on_raw_message_delete(self, payload):
        """Called when a message is deleted. 
        Unlike on_message_delete(), 
        this is called regardless of the message being in the internal message cache or not.

        payload -- RawMessageDeleteEvent, contains channel, guild and message id
        """
        pass

    async def on_raw_bulk_message_delete(self, payload):
        """Called when a bulk delete is triggered. 
        This event is called regardless of the message IDs being in the internal message cache or not.

        payload -- RawBulkMessageDeleteEvent, channel, guild and list of message ids
        """
        pass

    async def on_raw_reaction_add(self, payload):
        """Called when a reaction has a reaction added. 
        Unlike on_reaction_add(), 
        this is called regardless of the state of the internal message cache.

        payload -- RawReactionActionEvent, contains message, user, channel, guild id and the emoji used
        """
        pass

    async def on_raw_reaction_remove(self, payload):
        """Called when a reaction has a reaction removed. 
        Unlike on_reaction_remove(), 
        this is called regardless of the state of the internal message cache.

        payload -- RawReactionActionEvent, contains message, user, channel, guild id and the emoji used
        """
        pass

    async def on_raw_reaction_clear(self, payload):
        """Called when a message has all its reactions removed. 
        Unlike on_reaction_clear(), 
        this is called regardless of the state of the internal message cache.

        payload -- RawReactionClearEvent, contains message, channel and guild id
        """
        pass

def setup(bot):
    bot.add_cog(Events(bot))
