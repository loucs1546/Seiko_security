async def create_log_category_callback(self, interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Réservé aux administrateurs.", ephemeral=True)
        return

    # ✅ DÉBUT : Réponds immédiatement "en cours..."
    await interaction.response.defer(ephemeral=True)

    guild = interaction.guild
    for category in guild.categories:
        if "log" in category.name.lower() or "surveillance" in category.name.lower():
            await interaction.followup.send(
                f"❌ Une catégorie de logs existe déjà : **{category.name}**",
                ephemeral=True
            )
            return

    try:
        category = await guild.create_category(
            name="🔐・Surveillance",
            overwrites={
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
        )

        salon_configs = [
            ("📜・messages", "messages"),
            ("🎤・vocal", "vocal"),
            ("🎫・tickets", "tickets"),
            ("🛠️・commandes", "commands"),
            ("👑・rôles", "roles"),
            ("📛・profil", "profile"),
            ("🔍・contenu", "content"),
            ("🚨・alertes", "alerts")
        ]

        channel_ids = {}
        for name, key in salon_configs:
            channel = await guild.create_text_channel(name=name, category=category)
            channel_ids[key] = channel.id

        import core_config as config
        config.LOG_CHANNELS = channel_ids

        # ✅ FIN : Envoie le message final via followup
        await interaction.followup.send(
            f"✅ Catégorie **{category.name}** créée avec {len(salon_configs)} salons !",
            ephemeral=True
        )

    except Exception as e:
        await interaction.followup.send(f"❌ Erreur : {str(e)}", ephemeral=True)