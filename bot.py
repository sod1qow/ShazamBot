import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Command

from aiogram.dispatcher.storage import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage


from config import *
from btn import *
from states import *
from database import *


logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, parse_mode='html')
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)


async def command_menu(dp: Dispatcher):
  await dp.bot.set_my_commands(
    [
      types.BotCommand('start', 'Ishga tushirish'),
      types.BotCommand('admin', 'kanal qoshish'),
    ]
  )
  await create_tables()


@dp.message_handler(commands=['start'])
async def start_bot(message: types.Message):
    btn = await start_menu_btn()
    await message.answer("ShopUz Botga xush kelibsiz!", reply_markup=btn)


@dp.message_handler(text="Kategoriyalar")
async def show_category_handler(message: types.Message):
    category = await get_categories()
    btn = await category_btn(category)
    await message.answer("Kategoriyani tanlang:", reply_markup=btn)


@dp.message_handler(text="Ortga")
async def back_handler(message: types.Message):
    await start_bot(message)
    

@dp.message_handler(text="Admin bilan aloqa")
async def support_handler(message: types.Message):
  await message.answer("Bot admini: @admin")




  


@dp.callback_query_handler(text_contains="buy")
async def buy_product_callback(call: types.CallbackQuery, state: FSMContext):
  product_id = call.data.split(":")[-1]
  await state.update_data(product_id=product_id)
  
  await call.message.delete()
  await call.message.answer("Ismingizni kiriting: ")
  await BuyProductState.client_name.set()


@dp.message_handler(content_types=['text'], state=BuyProductState.client_name)
async def get_client_name_state(message: types.Message, state: FSMContext):
  await state.update_data(client_name=message.text)
  
  btn = await client_phone_btn()
  await message.answer("Telefon raqamingizni kiriting: ", reply_markup=btn)
  await BuyProductState.client_phone.set()


@dp.message_handler(content_types=['contact'], state=BuyProductState.client_phone)
async def get_client_phone_state(message: types.Message, state: FSMContext):
  await state.update_data(client_phone=message.contact.phone_number)
  
  btn = await client_geo_btn()
  await message.answer("Lokatsiyangizni yuboring: ", reply_markup=btn)
  await BuyProductState.client_geo.set()


@dp.message_handler(content_types=['location'], state=BuyProductState.client_geo)
async def get_client_geo_state(message: types.Message, state: FSMContext):
  geo_link = f"https://www.google.com/maps?q={message.location.latitude},{message.location.longitude}&ll={message.location.latitude},{message.location.longitude}&z=16"
  
  data = await state.get_data()
  product = await get_product_info(data['product_id'])
  context = f"ID: {message.from_user.id}\nIsm: {data['client_name']}\nTel.Raqam: {data['client_phone']}\n<a href='{geo_link}'>Lokatsiya</a>\n\nTovar nomi: {product[0]}\nRazmer: {product[1]}\nRangi: {product[2]}\nNarxi: {product[3]}"



  await bot.send_message(
    chat_id=-4088812365,
    text=context
  )

  await message.answer("✅ Buyurtmangiz qabul qilindi")
  await start_bot(message)
  

@dp.callback_query_handler(text_contains='prev')
async def prev_callback(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    prev_page = int(call.data.split(":")[-1])

    products = await state.get_data()
    prod = products['products'][prev_page]
    context = f"Nomi: {prod[0]}\nRazmer: {prod[1]}\nRangi: {prod[2]}\nNarxi: {prod[3]}"
    if call.message.caption != context:
        if prev_page > 0:
            btn = await product_btn(len(products['products']), prev_page - 1, prev_page+1, prev_page+1, prod[0])
        else:
            btn = await product_btn(len(products['products']), prev_page, prev_page+1, prev_page+1, prod[0])
        
        media = types.InputMediaPhoto(media=prod[-1], caption=context)
        await call.message.edit_media(media=media, reply_markup=btn)


@dp.callback_query_handler(text_contains='next')
async def next_callback(call: types.CallbackQuery, state: FSMContext):
    next_page = int(call.data.split(":")[-1])
    await call.answer()
    
    products = await state.get_data()
    if len(products['products']) != next_page:
      prod = products['products'][next_page]
      context = f"Nomi: {prod[0]}\nRazmer: {prod[1]}\nRangi: {prod[2]}\nNarxi: {prod[3]}"
      if call.message.caption != context:
          btn = await product_btn(len(products['products']), next_page-1, next_page+1, next_page+1, prod[0])
          
          media = types.InputMediaPhoto(media=prod[-1], caption=context)
          await call.message.edit_media(media=media, reply_markup=btn)




@dp.message_handler(commands=['admin'])
async def admin_panel_command(message: types.Message):
  user_id = message.from_user.id

  if user_id in ADMINS:
     btn = await admin_panel_btn()
     await message.answer("Siz admin panelidasiz:", reply_markup=btn)



@dp.callback_query_handler(text="back")
async def back_to_panel_callback(call: types.CallbackQuery):
  btn = await admin_panel_btn()
  await call.message.edit_text("Siz admin paneldasiz:", reply_markup=btn)

#fvvdx


@dp.callback_query_handler(text="add_channel")
async def add_channel_callback(call: types.CallbackQuery):
  channels = await get_channels()
  btn = await add_channel_btn(channels)
  await call.message.edit_text("Kanal qo`shish bo`limi:", reply_markup=btn)




@dp.message_handler(content_types=['text'])
async def get_cat_btn_handler(message: types.Message, state: FSMContext):
  products = await get_products(message.text)
  if products:
    await state.update_data(products=products)
  
    context = f"Nomi: {products[0][0]}\nRazmer: {products[0][1]}\nRangi: {products[0][2]}\nNarxi: {products[0][3]}"
  
    btn = await product_btn(
      total_pages=len(products), 
      prev_page=0, 
      next_page=1, 
      page=1, 
      product_id=products[0][0]
      )
    await message.answer_photo(products[0][-1], caption=context, reply_markup=btn)






if __name__ == "__main__":
  executor.start_polling(dp, on_startup=command_menu)