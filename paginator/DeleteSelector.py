# import discord
# class DeleteSelector(discord.ui.View):



#     @discord.ui.button(emoji="\U0001f5d1", disabled=True, row=2, style=discord.ButtonStyle.danger)
#     async def _delete_button_callback(self, interaction: discord.Interaction, pressed: discord.ui.Button):
#         self.children[2].disabled = False
#         await interaction.response.edit_message(content="Удаляю...")
#         results = await asyncio.gather(
#             *[delete_diagram(interaction, self._userIds[dia], dia) for dia in self._diagrams_to_delete] #TODO: SPAM!
#         )
#         if False in results:
#             await interaction.followup.send()

#     async def _delete_selector_callback(self, interaction: discord.Interaction, select: discord.ui.Select = None):
#     print(self.children[3].values)
#     if len(self.children[3].values) == 0:
#         self.children[2].disabled = True
#     else:
#         self.children[2].disabled = False

#     for option in self.children[3].options:
#         option.default = (option.value in self.children[3].values)

#     self._diagrams_to_delete = self.children[3].values
#     await interaction.response.edit_message(view=self)    