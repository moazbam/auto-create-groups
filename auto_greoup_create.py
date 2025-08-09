from pyrogram import Client, filters, types, enums
from pyrogram.errors import ListenerTimeout, PhoneCodeInvalid, PasswordHashInvalid, SessionPasswordNeeded
import asyncio
import os
import json
from threading import Timer, Thread
from datetime import datetime
import random


temp = {}
datas = {'status':False, 'apps':{}}


def IS_SPLIT(data):
    def func(flt, _, query: types.CallbackQuery):
        return flt.data == query.data.split("|")[0]
    
    return filters.create(func=func, data=data)


class Config:
    API_HASH : str = "dddce2b98453e66652b45657fd3cb649"
    API_ID   : str = "27457294"
    API_KEY  : str = ""
    SUDO     : str = 5724519766

os.makedirs("./.session", exist_ok=True)

if not os.path.exists("config.json"):
    with open("config.json", 'w', encoding='utf-8') as ioFile:
        json.dump({
            'data':{
                'groupCreateCount':0, 
                'createSleepHours':24, 
                'createCount':50
            },
            'chat':{},
            "session":{}, 
            "logchat":{},
            'history':{}
        }, ioFile, indent=3)

def getData():
    with open("config.json", 'r', encoding='utf-8') as ioFile:
        return json.load(ioFile)
    
def updateData(data: dict):
    with open("config.json", 'w', encoding='utf-8') as ioFile:
        json.dump(data, ioFile, indent=3)
    


app = Client(
    name="./.session/rad", 
    api_hash=Config.API_HASH, 
    api_id=Config.API_ID, 
    bot_token=Config.API_KEY, 
    parse_mode=enums.ParseMode.DEFAULT, 
)



### helpers
class Keyboards:
    def MAIN_KEYBOARD():
        botdata = getData()
        return types.InlineKeyboardMarkup([
            [
                types.InlineKeyboardButton(text="تشغيل ✅" if not datas['status'] else "ايقاف ☑️", callback_data="START_STATUS")
            ],
            [
                types.InlineKeyboardButton(text=f"CHAT : {'None' if not botdata['chat'] else botdata['chat']['title']}", 
                                        url="t.me/None" if not botdata['chat']  else f"t.me/{botdata['chat']['username']}"), 
                                        
                types.InlineKeyboardButton(text="تعين قناة الاشعارات", callback_data="SET_CHAT"),
            ], 
            [
                types.InlineKeyboardButton(text="اضافة حساب ", callback_data="ADD_ACCOUNT"), 
                types.InlineKeyboardButton(text="حذف حساب", callback_data="DELETE_ACCOUNT")
            ], 
            [
                types.InlineKeyboardButton(text="جلب بيانات المجموعات", callback_data="GREOUP_BACKUP")
            ]
        ])
    
    def BACK_MAIN():
        return types.InlineKeyboardMarkup([
            [
                types.InlineKeyboardButton(text="BACK", callback_data="back_main")
            ]
        ])
    
    def SELECT_ADD_SESSION_TYPE():
        return types.InlineKeyboardMarkup([
            [
                types.InlineKeyboardButton(text="ADD SESSION", callback_data="ADD_SESSION"),
                types.InlineKeyboardButton(text="ADD PHONE", callback_data="ADD_PHONE"),
            ], 
            [
                types.InlineKeyboardButton(text="BACK", callback_data="back_main")
            ]
        ])
    def DELETE_ACCOUNTS():
        keybaord = []
        botdata = getData()
        for sessionID, sessionDATA in botdata['session']:
            keybaord.append([
                types.InlineKeyboardButton(text=sessionID, callback_data="NIN"), 
                types.InlineKeyboardButton(text=sessionDATA['first_name'], url=f"t.me/{sessionDATA['username']}"), 
                types.InlineKeyboardButton(text="DELETE", callback_data=f"DELETE_SESSION|{sessionID}"), 
            ])
        if not botdata['session']:
            keybaord.append([types.InlineKeyboardButton(text="لا يوجد حسابات لي حذفها", callback_data="M")])

        keybaord.append(types.InlineKeyboardButton(text="BACK", callback_data="BACK"))
        return types.InlineKeyboardMarkup(keybaord)



@app.on_callback_query(filters.regex("^(back_main)$"))
@app.on_message(filters.private & filters.regex("^(/start$)"))
async def ON_START_BOT(app: Client, message: types.Message):
    if isinstance(message, types.CallbackQuery):
        await message.edit_message_text(
            text="- Welcome To Auto Make Groups Bot", 
            reply_markup=Keyboards.MAIN_KEYBOARD() 
        )
        return
    await message.reply(
        text="- Welcome To Auto Make Groups Bot", 
        reply_markup=Keyboards.MAIN_KEYBOARD()
    )



@app.on_callback_query(filters.regex("^ADD_ACCOUNT$"))
async def ON_ADD_SESSIONS(app: Client, query: types.CallbackQuery):
    await query.edit_message_text(
        text="⌔︙قم بي اختيار طريقة اضافة الحساب", 
        reply_markup=Keyboards.SELECT_ADD_SESSION_TYPE()
    )




@app.on_callback_query(IS_SPLIT("ADD_SESSION"))
async def ON_ADD_SESSION_STRING(app: Client, query: types.CallbackQuery):
    await query.edit_message_text(
        text="⌔︙قم بي ارسال جلسة pyrogram ", 
        reply_markup=Keyboards.BACK_MAIN()
    )

    try:
        data : types.Message = await app.listen(
            chat_id=query.message.chat.id,
            filters=filters.private & filters.text, 
            timeout=120
        )
    except ListenerTimeout as e:
        return 0
    sessionS = data.text
    tempApp = Client(
        name=":memory:", 
        api_hash=Config.API_HASH, 
        api_id=Config.API_ID, 
        session_string=sessionS,
        no_updates=True
    )

    try:
        await tempApp.connect()
        sessionData = await tempApp.get_me()
    except Exception as e:
        await data.reply(
            text="⌔︙الجلسة غير صالحة", 
            reply_markup=Keyboards.BACK_MAIN()
        )
        return
    

    botData = getData()
    botData['session'].update({sessionData.id: {
        'id':sessionData.id, 
        'first_name':sessionData.first_name, 
        'username':sessionData.username, 
        'password':None, 
        'session':sessionS, 
        'phone':sessionData.phone_number
    }})
    updateData(botData)

    await tempApp.disconnect()
    await data.reply(
        text="⌔︙تم اضافة الحساب بي نجاح", reply_markup=Keyboards.BACK_MAIN()
    )
    

@app.on_callback_query(IS_SPLIT("ADD_PHONE"))
async def ON_ADD_PHONE_STRING(app: Client, query: types.CallbackQuery):
    Password = None
    await query.edit_message_text(
        text="⌔︙قم بي ارسال رقم الهاتف.", 
        reply_markup=Keyboards.BACK_MAIN()
    )

    try:
        data : types.Message = await app.listen(
            chat_id=query.message.chat.id,
            filters=filters.private & filters.text, 
            timeout=120
        )
    except ListenerTimeout as e:
        return 0
    
    PHONE = data.text
    if not PHONE.strip("+").replace(' ', '').isdigit():
        await data.reply(
            text="⌔︙ لا يمكنك استخدام الاحرف الابجدية .", 
            reply_markup=Keyboards.BACK_MAIN()

        )
        return
    
    await asyncio.sleep(0.3)
    tempClient = Client(
        name=":memory:", 
        api_hash=Config.API_HASH,
        api_id=Config.API_ID, 
        in_memory=True,
        no_updates=True
    )
    
    
    await tempClient.connect()
    try:
        verCodeData = await tempClient.send_code(phone_number=PHONE)
    except Exception as e:
        await data.reply(
            text="⌔︙رقم الهاتف غير صالح .",
            reply_markup=Keyboards.BACK_MAIN()

        )
        return
    
    await data.reply(
        text="⌔︙ قم بي ارسال كود التحقق ."
    )

    try:
        data : types.Message = await app.listen(
            chat_id=query.message.chat.id,
            filters=filters.private & filters.text, 
            timeout=120
        )
    except ListenerTimeout as e:
        return 0
    
    verCode = data.text
    if not verCode.isdigit():
        await data.reply(
            text="⌔︙ لا يمكنك استخدام الاحرف الابجدية .", 
            reply_markup=Keyboards.BACK_MAIN()

        )
        return
    
    try:
        await tempClient.sign_in(
            phone_code=verCode, 
            phone_number=PHONE, 
            phone_code_hash=verCodeData.phone_code_hash
        )
    except PhoneCodeInvalid as e:
        await data.reply(
            text="⌔︙رمز التحقق غير صالح .", 
            reply_markup=Keyboards.BACK_MAIN()

        )
        return
    except SessionPasswordNeeded as e:
        await data.reply(
            text="⌔︙قم بي ارسال كلمة مرور التحقق بي خطوتين ."

        )

        try:
            data : types.Message = await app.listen(
                chat_id=query.message.chat.id,
                filters=filters.private & filters.text, 
                timeout=120
            )
        except ListenerTimeout as e:
            await tempClient.disconnect()
            return 0

        Password = data.text
        try:
            await tempClient.check_password(Password)
        except PasswordHashInvalid as e:
            await data.reply(
                text="⌔︙كلمت المرور غير صالحة.", 
                reply_markup=Keyboards.BACK_MAIN()

            )
            await tempClient.disconnect()
            return
        except Exception as e:
            print(e)
            await data.reply(
                text="⌔︙خطاء غير معروف .",
                reply_markup=Keyboards.BACK_MAIN()

            )
            await tempClient.disconnect()
            return
    
    except Exception as e:
        await data.reply(
            text="⌔︙خطاء غير معروف .", 
            reply_markup=Keyboards.BACK_MAIN()

        )
        print(e)
        await tempClient.disconnect()
        return
    
    sessionData = await tempClient.get_me()
    session = await tempClient.export_session_string()

    botData = getData()
    botData['session'].update({sessionData.id: {
        'id':sessionData.id, 
        'first_name':sessionData.first_name, 
        'username':sessionData.username, 
        'password':None, 
        'session':session, 
        'phone':sessionData.phone_number
    }})
    updateData(botData)
    await tempClient.disconnect()
    await data.reply(
        text="⌔︙تم اضافة الحساب بي نجاح", reply_markup=Keyboards.BACK_MAIN()
    )




@app.on_callback_query(filters.regex("^SET_CHAT$"))
async def ON_SET_CHAT(app: Client, query: types.CallbackQuery):
    await query.edit_message_text(
        text="- قم بي رفع البوت مشرف في الدردشة و ارسل الايدي او المعرف", 
        reply_markup=Keyboards.BACK_MAIN()
    )

    try:
        data : types.Message = await app.listen(
            chat_id=query.message.chat.id, 
            filters=filters.private & filters.text, 
            timeout=60
        )
    except ListenerTimeout as e:
        pass

    PERR = data.text if not str(data).strip("-").isdigit() else int(data.text)


    try:
        chatdata = await app.get_chat(PERR)
    except Exception as e:
        print(e)
        await data.reply(
            text="- معرف القناة غير صالح او البوت غير مشرف", 
            reply_markup=Keyboards.BACK_MAIN()
        )
        return
    if chatdata.type not in [enums.ChatType.CHANNEL, enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        await data.reply(
            text="- نوع الدردشة غير صالح .", 
            reply_markup=Keyboards.BACK_MAIN()
        )
        return

    try:
        botChatStatus = await app.get_chat_member(PERR, app.me.id)
    except Exception as e:
        print(e)
        await data.reply(
            text="- معرف القناة غير صالح او البوت غير مشرف", 
            reply_markup=Keyboards.BACK_MAIN()
        )
        return
    if botChatStatus.status != enums.ChatMemberStatus.ADMINISTRATOR:
        await data.reply(
            text="- عذرن البوت غير مشرف في القناة او المجموعة", 
            reply_markup=Keyboards.BACK_MAIN()
        )
        return
    

    botdata = getData()
    botdata['chat']['id'] = chatdata.id
    botdata['chat']['title'] = chatdata.title or chatdata.first_name
    botdata['chat']['username'] = chatdata.username
    botdata['chat']['type'] = str(chatdata.type)
    updateData(botdata)

    await data.reply(
            text="- تم تعين قناة الاشعارات بي نجاح.", 
            reply_markup=Keyboards.BACK_MAIN()
        )



@app.on_callback_query(filters.regex("^(DELETE_ACCOUNT)$"))
async def ON_SHOW_ACCOUNT(app: Client, query: types.CallbackQuery):
    await query.edit_message_text(
        text="- اليك قائمة الحسابات لي حذفها",
        reply_markup=Keyboards.DELETE_ACCOUNTS()
    )

@app.on_callback_query(IS_SPLIT("DELETE_SESSION"))
async def ON_DELETE_SESSION(app: Client, query: types.CallbackQuery):
    sessionID = query.data.split("|")[1]
    botData = getData()
    botData['session'].pop(sessionID)
    updateData(botData)
    await query.answer(text="- تم حذف الحساب بي نجاح ✅.")

    await query.edit_message_text(
        text="- اليك قائمة الحسابات لي حذفها",
        reply_markup=Keyboards.DELETE_ACCOUNTS()
    )  

@app.on_callback_query(filters.regex("^(GREOUP_BACKUP)$"))
async def ON_CLAER_DATA(app: Client, query: types.CallbackQuery):
    Botdata = getData()
    with open("history.json", 'w', encoding='utf-8') as ioFILE:
        json.dump(Botdata['history'], ioFILE, indent=3)
    
    await query.edit_message_media(
        media=types.InputMediaDocument(
            media='history.json', 
            caption="- النسخة تحتوي على جميع بيانات المجموعات التي تم انشائها"
        )
    )
    os.remove("history.json")


async def CRETAE_THREAD(app: Client):
    data = getData()
    if not datas['status']:
        return

    groupsData = {
        "sessionCount":len(data['session']), 
        "GroupCount":0,
        "sessions":{}
    }
    x = 0
    for ID, tapp in datas['apps'].items():
        sessionGroup = []
        for i in range(data['data']['createCount']):
            await asyncio.sleep(0.8)
            title_ = f"{datetime.now().strftime('%d-%m-%Y')} #{i}"
            try:
                groupData = await tapp.create_supergroup(
                    title_, 
                    "ᴛᴇʟᴇɢʀᴀᴍ ᴀᴜᴛᴏ ɢʀᴇᴏᴜᴘ ᴄʀᴇᴀᴛᴇ ᴘᴏᴡᴇʀ ʙʏ ʀᴀɪᴅ\nᴛᴇʟᴇɢʀᴀᴍ: @r_afx  ᴄʜᴀɴɴᴇʟ: @radfx2"
                )
            except Exception as e:
                print(e)
                break 
            try:
                groupLINK = await tapp.create_chat_invite_link(chat_id=groupData.id)
                groupInvLink = groupLINK.invite_link
            except Exception as e:
                print(e)
                groupInvLink = None

            await tapp.send_message(
                groupData.id, 
                title_
            )
            for i in range(15):
                await asyncio.sleep(0.3)
                await tapp.send_message(
                    groupData.id, 
                text="".join([random.choice("ABCDEFGHUJKLMNOPQRSTUVWXYZ") for i in range(9)])
            )
                
            await tapp.leave_chat(chat_id=groupData.id, delete=True)             
            sessionGroup.append({
                'id':groupData.id, 
                'title':title_, 
                'link':groupInvLink
            })
            x+=1
        groupsData['sessions'][ID] = sessionGroup

    groupsData['GroupCount'] = x
    data['history'][datetime.now().strftime("%d-%m-%Y")] = groupsData
    data['data']['groupCreateCount']+=x

    updateData(data)
    if not data['chat'] is None:
        await app.send_message(
            chat_id=data['chat']['id'],
            text=f"""
                - **Create Group On Date** {datetime.now().strftime("%d-%m-%Y")} Done
                - **Create Group Count** : {x}
                - **Session Count** : {len(data['session'])}
            """
        )
        mes = ""
        for sessionID ,groups in groupsData['sessions'].items():
            for group in groups:
                mes+="- **session** :[{}](tg://user?id={}) \n- **date** : {} \n- **link** : {}\n".format(
                    data['session'][sessionID]['first_name'], 
                    sessionID, 
                    group['title'],
                    group['link']
                )
                mes+='============\n'
                
        # sned message 
        await app.send_message(
            chat_id=data['chat']['id'], 
            text=mes
        )
    else :
        await app.send_message(
            chat_id=Config.SUDO,
            text=f"""
                - **Create Group On Date** {datetime.now().strftime("%d-%m-%Y")} Done
                - **Create Group Count** : {x}
                - **Session Count** : {len(data['session'])}
            """
        )

    Timer(data['data']['createSleepHours'] * 60 * 60, asyncio.run, args=(CRETAE_THREAD(app), )).start()



async def CREATE_HANDLER(app: Client):
    data = getData()
    # check Start session
    for sessionID, sessionData in data['session'].items():
        if sessionID in datas['apps']:
            continue
        datas['apps'][sessionID] = Client(
            sessionID, 
            session_string=sessionData['session'], 
            no_updates=True
        )

        try:
            await datas['apps'][sessionID].connect()
            datas['apps'][sessionID].me = await datas['apps'][sessionID].get_me()
        except Exception  as e:
            print(e)
            continue

    Time = Timer(10 , asyncio.run, args=(CRETAE_THREAD(app), )).start()




@app.on_callback_query(filters.regex("^START_STATUS$"))
async def ON_START_STATUS(app: Client, query: types.CallbackQuery):
    if datas['status']:
        datas['status'] = False
        await query.edit_message_text(
            text="- تم ايقاف البوت بي نجاح", 
            reply_markup=Keyboards.BACK_MAIN()
        )
        return
    botData = getData()
    if not botData['session']:
        await query.edit_message_text(
            text="- عذرن لا يوجد حسابات بي بدء العملية", 
            reply_markup=Keyboards.BACK_MAIN()
        )
        return

    datas['status'] = True
    Thread(target=asyncio.run , args=(CREATE_HANDLER(app), )).start()
    await query.edit_message_text(
            text="- تم تشغيل البوت بي نجاح", 
            reply_markup=Keyboards.BACK_MAIN()
        )

if __name__ == "__main__":
    asyncio.run(app.run())