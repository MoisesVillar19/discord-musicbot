"""Views genéricas (Sprint 12).

Unifican los 3 menús de encolar (play/troll/history) y los 2 paginadores
(queue/lyrics): cada comando solo aporta opciones + qué hacer al elegir.
"""

import discord


class EnqueueSelectView(discord.ui.View):
    """Menú select que entrega lo elegido. Solo el solicitante puede usarlo.

    options: lista de (label, description, payload).
    on_timeout_edit: (interaction_original, texto) para avisar expiración.
    """

    def __init__(
        self,
        *,
        options: list,
        requester_id: int,
        on_pick,
        placeholder: str = "Elige…",
        timeout: float = 60,
        on_timeout_edit=None,
    ):
        super().__init__(timeout=timeout)
        self._options = options
        self._requester_id = requester_id
        self._on_pick = on_pick
        self._on_timeout_edit = on_timeout_edit
        select = discord.ui.Select(
            placeholder=placeholder,
            options=[
                discord.SelectOption(
                    label=label[:100], value=str(i), description=(desc or "")[:100]
                )
                for i, (label, desc, _payload) in enumerate(options)
            ],
        )
        select.callback = self._select_callback
        self.add_item(select)

    async def _select_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self._requester_id:
            return await interaction.response.send_message(
                "❌ Solo quien pidió puede elegir.", ephemeral=True
            )
        values = (interaction.data or {}).get("values", [])
        try:
            index = int(values[0])
            _label, _desc, payload = self._options[index]
        except (IndexError, TypeError, ValueError):
            return await interaction.response.send_message("❌ Opción inválida.", ephemeral=True)
        await self._on_pick(interaction, index, payload)

    async def on_timeout(self):
        if not self._on_timeout_edit:
            return
        interaction, text = self._on_timeout_edit
        try:
            await interaction.edit_original_response(content=text, view=None)
        except Exception:
            pass


class PagerView(discord.ui.View):
    """Paginador ⬅️/➡️ genérico. render(page) -> discord.Embed."""

    def __init__(self, *, total_pages: int, render, timeout: float = 120):
        super().__init__(timeout=timeout)
        self.page = 1
        self._total_pages = max(1, total_pages)
        self._render = render
        self._sync_buttons()

    def _sync_buttons(self):
        self.prev_btn.disabled = self.page <= 1
        self.next_btn.disabled = self.page >= self._total_pages

    async def _goto(self, interaction: discord.Interaction, page: int):
        self.page = min(self._total_pages, max(1, page))
        self._sync_buttons()
        await interaction.response.edit_message(embed=self._render(self.page), view=self)

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary)
    async def prev_btn(self, interaction: discord.Interaction, button):
        await self._goto(interaction, self.page - 1)

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.secondary)
    async def next_btn(self, interaction: discord.Interaction, button):
        await self._goto(interaction, self.page + 1)
