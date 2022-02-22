import discord
import time
from dotenv import load_dotenv
import os

import log_writter
import order_notifer

client = discord.Client()
final_msg = []
base_dir = os.path.abspath(os.path.dirname(__file__))
mode = "ready"
current_order = {}
order_info = ""
final_msg_type = []
channel = []
testing = False


@client.event
async def on_ready():
    music = discord.Activity(type=discord.ActivityType.playing, name="Beta測試階段")
    await client.change_presence(status=discord.Status.online, activity=music)
    log_writter.write_log("-------------------------------------------------------------\n", True)
    log_writter.write_log("\n登入成功！\n目前登入身份：" +
                          str(client.user) + "\n以下為使用紀錄(只要開頭訊息有\"ao!\"，則這則訊息和系統回應皆會被記錄)：\n\n")


@client.event
async def on_message(message):
    global final_msg, final_msg_type, mode, current_order, order_info, channel, testing
    msg_in = str(message.content)
    localtime = time.localtime()
    time_stamp = time.strftime("%Y/%m/%d  %p  %I:%M:%S", localtime)
    if message.author == client.user:
        return
    elif msg_in == "ao!test":
        if testing:
            testing = False
            embed = discord.Embed(title="測試結束", description="測試模式已關閉。", color=0xF2E011)
            embed.set_footer(text=time_stamp)
            final_msg.append(embed)
            final_msg_type.append("embed")
            channel.append(message.channel)
        else:
            testing = True
            embed = discord.Embed(title="測試開始", description="測試模式已開啟。", color=0xF2E011)
            embed.set_footer(text=time_stamp)
            final_msg.append(embed)
            final_msg_type.append("embed")
            channel.append(message.channel)
        use_log = str(message.channel) + "/" + str(message.author) + ":\n" + msg_in + "\n\n"
        log_writter.write_log(use_log)
    elif testing:
        return
    elif msg_in.startswith("ao!"):
        use_log = str(message.channel) + "/" + str(message.author) + ":\n" + msg_in + "\n\n"
        log_writter.write_log(use_log)
        if msg_in[3:] == "help":
            embed = discord.Embed(title="協助", description="本機器人正在開發中，敬請期待！", color=0x14E073)
            embed.add_field(name="`help`", value="顯示此協助訊息。", inline=True)
            embed.add_field(name="`ping`", value="檢查本機器人延遲狀態。", inline=True)
            embed.add_field(name="`add`", value="新增訂單。", inline=True)
            embed.add_field(name="`edit`", value="編輯訂單。", inline=True)
            embed.set_footer(text=time_stamp)
            final_msg.append(embed)
            final_msg_type.append("embed")
            channel.append(message.channel)
        elif msg_in[3:] == "ping":
            embed = discord.Embed(title="延遲", description="{0}ms".format(str(round(client.latency * 1000))),
                                  color=0x14E073)
            embed.set_footer(text=time_stamp)
            final_msg.append(embed)
            final_msg_type.append("embed")
            channel.append(message.channel)
        elif msg_in[3:6] == "add":
            if "busy" not in mode:
                current_order["author"] = str(message.author)
                mode = "busy-1"
                music = discord.Activity(type=discord.ActivityType.playing, name="處理訂單中...")
                await client.change_presence(status=discord.Status.dnd, activity=music)
                embed = discord.Embed(title="新增訂單", description="請貼上**要求商品的URL(連結)**，然後送出。", color=0x14E073)
                last_num_txt = open("last-num.txt", mode="r", encoding="utf-8")
                num = str(last_num_txt.read())
                num = int(num) + 1
                last_num_txt.close()
                order_num = "AO-{0}".format(str(num))
                current_order["order_num"] = order_num
                embed.add_field(name="訂單編號", value=order_num, inline=False)
                embed.set_footer(text="輸入n以取消 • " + time_stamp)
                final_msg.append(embed)
                final_msg_type.append("embed")
                channel.append(message.channel)
                last_num_txt = open("last-num.txt", mode="w", encoding="utf-8")
                last_num_txt.write(str(num))
                last_num_txt.close()
            else:
                embed = discord.Embed(title="錯誤：新增訂單", description="目前系統忙碌中，請稍後再試。", color=0xf21c1c)
                embed.set_footer(text=time_stamp)
                final_msg.append(embed)
                final_msg_type.append("embed")
                channel.append(message.channel)
        elif msg_in[3:7] == "edit":
            if "busy" not in mode:
                current_order["author"] = str(message.author)
                mode = "busy-e-1"
                music = discord.Activity(type=discord.ActivityType.playing, name="處理訂單中...")
                await client.change_presence(status=discord.Status.dnd, activity=music)
                embed = discord.Embed(title="編輯訂單", description="請輸入**訂單編號**(ex:`AO-1`)。", color=0x14E073)
                embed.set_footer(text="輸入n以取消 • " + time_stamp)
                final_msg.append(embed)
                final_msg_type.append("embed")
                channel.append(message.channel)
            else:
                embed = discord.Embed(title="錯誤：編輯訂單", description="目前系統忙碌中，請稍後再試。", color=0xf21c1c)
                embed.set_footer(text=time_stamp)
                final_msg.append(embed)
                final_msg_type.append("embed")
                channel.append(message.channel)
    elif "busy" in mode:
        if current_order["author"] == str(message.author):
            use_log = str(message.channel) + "/" + str(message.author) + ":\n" + msg_in + "\n\n"
            log_writter.write_log(use_log)
            if msg_in == "n":
                music = discord.Activity(type=discord.ActivityType.playing, name="Beta測試階段")
                await client.change_presence(status=discord.Status.online, activity=music)
                embed = discord.Embed(title="已取消操作", description="操作已取消！", color=0x14E073)
                embed.set_footer(text=time_stamp)
                final_msg.append(embed)
                final_msg_type.append("embed")
                channel.append(message.channel)
                mode = "ready"
                current_order = {}
            elif mode == "busy-1":
                if msg_in.startswith("http"):
                    mode = "busy-2"
                    current_order["url"] = msg_in
                    embed = discord.Embed(title="新增訂單", description="已新增！請輸入**商品數量**。", color=0x14E073)
                    embed.set_footer(text=time_stamp)
                    final_msg.append(embed)
                    final_msg_type.append("embed")
                    channel.append(message.channel)
                else:
                    embed = discord.Embed(title="錯誤：新增訂單", description="請輸入**要求商品的URL(連結)**。", color=0xf21c1c)
                    embed.set_footer(text=time_stamp)
                    final_msg.append(embed)
                    final_msg_type.append("embed")
                    channel.append(message.channel)
            elif mode == "busy-2":
                if msg_in.isdigit():
                    mode = "busy-3"
                    current_order["amount"] = msg_in
                    embed = discord.Embed(title="新增訂單", description="已確認！請確認下方訂單內容是否正確。", color=0x14E073)
                    embed.set_footer(text=time_stamp)
                    final_msg.append(embed)
                    final_msg_type.append("embed")
                    channel.append(message.channel)
                    embed = discord.Embed(title="訂單內容：`{0}`".format(str(current_order["order_num"])),
                                          description="商品網址：{0}\n商品數量：{1}".format(
                                              str(current_order["url"]), str(current_order["amount"])),
                                          color=0x14E073)
                    embed.set_footer(text=time_stamp)
                    final_msg.append(embed)
                    final_msg_type.append("embed")
                    channel.append(message.channel)
                    embed = discord.Embed(title="確認訂單", description="請輸入`y`表示**確認**。或是輸入`n`，以**取消**這次訂單。",
                                          color=0x14E073)
                    final_msg.append(embed)
                    final_msg_type.append("embed")
                    channel.append(message.channel)
                else:
                    embed = discord.Embed(title="錯誤：新增訂單", description="請輸入整數。", color=0xf21c1c)
                    embed.set_footer(text=time_stamp)
                    final_msg.append(embed)
                    final_msg_type.append("embed")
                    channel.append(message.channel)
            elif mode == "busy-3":
                if msg_in == "y" or "Y":
                    music = discord.Activity(type=discord.ActivityType.playing, name="Beta測試階段")
                    await client.change_presence(status=discord.Status.online, activity=music)
                    order_txt_path = base_dir + "\\order-database\\" + str(current_order["order_num"]) + ".txt"
                    order_txt = open(order_txt_path, mode="a", encoding="utf-8")
                    order_txt.write(str(current_order))
                    order_txt.close()
                    embed = discord.Embed(title="已確認訂單",
                                          description="訂單已確認！\n請記得你的訂單編號：**{0}**，以便後續的確認！".format(
                                              current_order["order_num"]), color=0x14E073)
                    embed.set_footer(text=time_stamp)
                    final_msg.append(embed)
                    final_msg_type.append("embed")
                    channel.append(message.channel)
                    order_info = order_notifer.new_order_notice(current_order["order_num"])
                    mode = "ready"
                    current_order = {}
            elif mode == "busy-e-1":
                if not msg_in.startswith("AO-"):
                    embed = discord.Embed(title="錯誤：查詢訂單", description="請輸入**訂單編號(AO-XX)**。", color=0xf21c1c)
                    embed.set_footer(text="輸入n以取消 • " + time_stamp)
                    final_msg.append(embed)
                    final_msg_type.append("embed")
                    channel.append(message.channel)
                else:
                    try:
                        order_txt_path = base_dir + "\\order-database\\" + msg_in + ".txt"
                        order_txt = open(order_txt_path, mode="r", encoding="utf-8")
                        current_order = str(order_txt.read())
                        current_order = eval(current_order)
                        order_txt.close()
                        if current_order["author"] == str(message.author):
                            embed = discord.Embed(title="訂單內容", description="訂單編號：{0}".format(str(msg_in)),
                                                  color=0x14E073)
                            embed.add_field(name=":one: 商品連結", value=current_order["url"], inline=False)
                            embed.add_field(name=":two: 商品數量", value=current_order["amount"], inline=False)
                            embed.set_footer(text=time_stamp)
                            final_msg.append(embed)
                            final_msg_type.append("embed")
                            channel.append(message.channel)
                            embed = discord.Embed(title="選擇編輯欄位", description="請輸入要編輯的**欄位編號**。", color=0x14E073)
                            embed.set_footer(text="輸入n以取消 • " + time_stamp)
                            mode = "busy-e-2"
                        else:
                            embed = discord.Embed(title="錯誤：編輯訂單", description="訂單編號：`{0}`，並非您的訂單。".format(str(msg_in)),
                                                  color=0xf21c1c)
                            embed.set_footer(text="輸入n以取消 • " + time_stamp)
                            # problem here
                        final_msg.append(embed)
                        final_msg_type.append("embed")
                        channel.append(message.channel)
                    except FileNotFoundError:
                        embed = discord.Embed(title="錯誤：編輯訂單", description="訂單編號`{0}`不存在！".format(msg_in),
                                              color=0xf21c1c)
                        embed.set_footer(text="輸入n以取消 • " + time_stamp)
                        final_msg.append(embed)
                        final_msg_type.append("embed")
                        channel.append(message.channel)
            elif mode == "busy-e-2":
                if msg_in.isdigit():
                    if int(msg_in) == 1:
                        embed = discord.Embed(title="編輯訂單：`{0}`".format(current_order["order_num"]),
                                              description="請輸入新的商品連結。", color=0x14E073)
                        embed.set_footer(text="輸入n以取消 • " + time_stamp)
                        final_msg.append(embed)
                        final_msg_type.append("embed")
                        channel.append(message.channel)
                        mode = "busy-e-3"
                    elif int(msg_in) == 2:
                        embed = discord.Embed(title="編輯訂單：`{0}`".format(current_order["order_num"]),
                                              description="請輸入新的商品數量。", color=0x14E073)
                        embed.set_footer(text="輸入n以取消 • " + time_stamp)
                        final_msg.append(embed)
                        final_msg_type.append("embed")
                        channel.append(message.channel)
                        mode = "busy-e-4"
                    else:
                        embed = discord.Embed(title="錯誤：編輯訂單", description="請輸入**欄位編號(1或2)**。", color=0xf21c1c)
                        embed.set_footer(text="輸入n以取消 • " + time_stamp)
                        final_msg.append(embed)
                        final_msg_type.append("embed")
                        channel.append(message.channel)
                else:
                    embed = discord.Embed(title="錯誤：編輯訂單", description="請輸入**欄位編號(1或2)**。", color=0xf21c1c)
                    embed.set_footer(text="輸入n以取消 • " + time_stamp)
                    final_msg.append(embed)
                    final_msg_type.append("embed")
                    channel.append(message.channel)
            elif mode == "busy-e-3":
                if msg_in.startswith("http"):
                    current_order["url"] = msg_in
                    embed = discord.Embed(title="編輯訂單：`{0}`".format(current_order["order_num"]),
                                          description="已經編輯了商品連結。", color=0x14E073)
                    embed.add_field(name="商品連結", value=current_order["url"], inline=False)
                    embed.add_field(name="商品數量", value=current_order["amount"], inline=False)
                    embed.set_footer(text=time_stamp)
                    final_msg.append(embed)
                    final_msg_type.append("embed")
                    channel.append(message.channel)
                    order_txt_path = base_dir + "\\order-database\\" + str(current_order["order_num"]) + ".txt"
                    order_txt = open(order_txt_path, mode="w", encoding="utf-8")
                    order_txt.write(str(current_order))
                    order_txt.close()
                    music = discord.Activity(type=discord.ActivityType.playing, name="Beta測試階段")
                    await client.change_presence(status=discord.Status.online, activity=music)
                    mode = "ready"
                    order_info = order_notifer.new_order_notice(current_order["order_num"], True)
                else:
                    embed = discord.Embed(title="錯誤：編輯訂單", description="請輸入正確的**商品連結**。", color=0xf21c1c)
                    embed.set_footer(text="輸入n以取消 • " + time_stamp)
                    final_msg.append(embed)
                    final_msg_type.append("embed")
                    channel.append(message.channel)
            elif mode == "busy-e-4":
                if msg_in.isdigit():
                    current_order["amount"] = msg_in
                    embed = discord.Embed(title="編輯訂單：`{0}`".format(current_order["order_num"]),
                                          description="已經編輯了商品數量。", color=0x14E073)
                    embed.add_field(name="商品連結", value=current_order["url"], inline=False)
                    embed.add_field(name="商品數量", value=current_order["amount"], inline=False)
                    embed.set_footer(text=time_stamp)
                    final_msg.append(embed)
                    final_msg_type.append("embed")
                    channel.append(message.channel)
                    order_txt_path = base_dir + "\\order-database\\" + str(current_order["order_num"]) + ".txt"
                    order_txt = open(order_txt_path, mode="w", encoding="utf-8")
                    order_txt.write(str(current_order))
                    order_txt.close()
                    music = discord.Activity(type=discord.ActivityType.playing, name="Beta測試階段")
                    await client.change_presence(status=discord.Status.online, activity=music)
                    mode = "ready"
                    order_info = order_notifer.new_order_notice(current_order["order_num"], True)
                else:
                    embed = discord.Embed(title="錯誤：編輯訂單", description="請輸入正確的**商品數量**。", color=0xf21c1c)
                    embed.set_footer(text="輸入n以取消 • " + time_stamp)
                    final_msg.append(embed)
                    final_msg_type.append("embed")
                    channel.append(message.channel)
    if order_info != "":
        final_msg.append("<@657519721138094080>")
        final_msg_type.append("normal")
        channel.append(client.get_channel(942379971345797151))
        final_msg.append(order_info)
        final_msg_type.append("embed")
        channel.append(client.get_channel(942379971345797151))
        channel.append(message.channel)
        order_info = ""
    for i in range(len(final_msg)):
        if final_msg_type[i] == "embed":
            await channel[i].send(embed=final_msg[i])
        else:
            await channel[i].send(final_msg[i])
        new_log = str(channel[i]) + "/" + str(client.user) + ":\n" + str(final_msg[i]) + "\n\n"
        log_writter.write_log(new_log)
    final_msg = []
    channel = []
    final_msg_type = []

env_path = "TOKEN.env"
load_dotenv(dotenv_path=os.path.join(base_dir, "TOKEN.env"))
TOKEN = str(os.getenv("TOKEN"))
client.run(TOKEN)
