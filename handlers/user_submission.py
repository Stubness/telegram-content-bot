from aiogram import Dispatcher, types
from config import ADMIN_ID, CHANNEL_ID

def register_handlers(dp: Dispatcher):
    @dp.message(lambda msg: msg.photo or msg.video or msg.text)
    async def handle_submission(message: types.Message):
        print("📥 handle_submission сработал")

        sender = message.from_user.username or message.from_user.full_name or "unknown"
        sender_id = message.from_user.id
        caption = message.caption or message.text or "(no text)"

        print(f"👤 Сообщение от: {sender} (ID: {sender_id})")
        print(f"📝 Caption/Text: {caption}")

        try:
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="✅ Publish",
                        callback_data=f"approve|{sender}|{message.message_id}"
                    ),
                    types.InlineKeyboardButton(
                        text="❌ Reject",
                        callback_data="reject"
                    )
                ]
            ])

            print(f"📤 Пытаюсь переслать админу ({ADMIN_ID})...")
            forwarded = await message.send_copy(chat_id=ADMIN_ID)
            await forwarded.reply(
                f"Submitted by @{sender}:\n\n{caption}",
                reply_markup=keyboard
            )
            print("✅ Переслано админу")

            # 👇 Вот это добавлено: обратная связь пользователю
            await message.reply("✅ Thank you! Your content has been submitted for review.")

        except Exception as e:
            print(f"❌ Ошибка при пересылке админу: {e}")

    @dp.callback_query()
    async def handle_callback(callback: types.CallbackQuery):
        data = callback.data
        if data.startswith("approve"):
            _, sender, _ = data.split("|")
            original = callback.message.reply_to_message
            caption = original.caption or original.text or ""

            try:
                print(f"📤 Публикую в канал: {CHANNEL_ID}")
                if original.photo:
                    await callback.bot.send_photo(
                        chat_id=CHANNEL_ID,
                        photo=original.photo[-1].file_id,
                        caption=f"📨 From @{sender}:\n\n{caption}"
                    )
                elif original.video:
                    await callback.bot.send_video(
                        chat_id=CHANNEL_ID,
                        video=original.video.file_id,
                        caption=f"📨 From @{sender}:\n\n{caption}"
                    )
                elif original.text:
                    await callback.bot.send_message(
                        chat_id=CHANNEL_ID,
                        text=f"📨 From @{sender}:\n\n{caption}"
                    )

                await callback.message.edit_text("✅ Published to channel")
                print("✅ Успешно опубликовано")
            except Exception as e:
                print(f"❌ Ошибка при публикации в канал: {e}")
                await callback.message.edit_text("❌ Failed to publish")
        elif data == "reject":
            await callback.message.edit_text("❌ Rejected")
