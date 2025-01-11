from discord_webhook import DiscordWebhook, DiscordEmbed

import time

Config = None
Webhook = None

def LoadConfig(NewConfig):
    global Config
    Config = NewConfig

def SendWebhook(Data):
    # Unpack Config
    Urls = Config["Webhook_Urls"]

    EmbedConfig = Config["Embed"]
    Title = EmbedConfig["Title"]
    Description = EmbedConfig["Description"]
    Color = EmbedConfig["Color"]
    Inline = EmbedConfig["Inline"]

    # Create Embed attachment
    Embed = DiscordEmbed(title=Title, description=Description, color=Color)
    Embed.set_footer(text="Depso Account generator")

    Unix = int(time.time())
    Data["Created at"] = f"<t:{Unix}:D>"

    # Unpack data
    for Key in Data:
        Value = Data[Key]
        Embed.add_embed_field(name=Key, value=Value, inline=Inline)

    # Send message to webhooks
    for Url in Urls:
        Message = DiscordWebhook(url=Url, rate_limit_retry=True)
        Message.add_embed(Embed)

        try:
            Message.execute()
        except Exception as err:
            print("Webhook failed to send!")
            print(err)