import discord
import time
from dotenv import load_dotenv
import os

import log_writter
import order_notifer

client = discord.Client()
localtime = time.localtime()
final_msg = []
time_stamp = time.strftime("%Y/%m/%d  %H:%M:%S  %z", localtime)
base_dir = os.path.abspath(os.path.dirname(__file__))
mode = "ready"
current_order = {}
order_info = ""


@client.event
async def on_ready():
    music = discord.Activity(type=discord.ActivityType.playing, name="Alpha測試階段")
    await client.change_presence(status=discord.Status.online, activity=music)
    log_writter.write_log("-------------------------------------------------------------\n", True)
    log_writter.write_log("\n登入成功！\n目前登入身份：" +
                          str(client.user) + "\n以下為使用紀錄(只要開頭訊息有\"ao!\"，則這則訊息和系統回應皆會被記錄)：\n\n")


@client.event
async def on_message(message):
    global final_msg, time_stamp, mode, current_order, order_info
    msg_in = message.content
    if message.author == client.user:
        return
    elif msg_in.startswith("ao!"):
        use_log = str(message.channel) + "/" + str(message.author) + ":\n" + msg_in + "\n\n"
        log_writter.write_log(use_log)
        if msg_in[3:] == "help":
            embed = discord.Embed(title="協助", description="本機器人正在開發中，敬請期待！", color=0x14E073)
            embed.set_footer(text=time_stamp)
            final_msg.append(embed)
        if msg_in[3:] == "ping":
            embed = discord.Embed(title="延遲", description="{0}ms".format(str(round(client.latency * 1000))),
                                  color=0x14E073)
            embed.set_footer(text=time_stamp)
            final_msg.append(embed)
        if msg_in[3:6] == "add":
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
                embed.set_footer(text=time_stamp)
                final_msg.append(embed)
                last_num_txt = open("last-num.txt", mode="w", encoding="utf-8")
                last_num_txt.write(str(num))
                last_num_txt.close()
            else:
                embed = discord.Embed(title="錯誤：新增訂單", description="目前系統忙碌中，請稍後再試。", color=0xf21c1c)
                embed.set_footer(text=time_stamp)
                final_msg.append(embed)
    elif "busy" in mode:
        if current_order["author"] == str(message.author):
            use_log = str(message.channel) + "/" + str(message.author) + ":\n" + msg_in + "\n\n"
            log_writter.write_log(use_log)
            if msg_in.startswith("http://") or msg_in.startswith("https://"):
                if mode == "busy-1":
                    mode = "busy-2"
                    current_order["url"] = msg_in
                    embed = discord.Embed(title="新增訂單", description="已新增！請輸入**商品數量**。", color=0x14E073)
                    embed.set_footer(text=time_stamp)
                    final_msg.append(embed)
            elif msg_in.isdigit():
                if mode == "busy-2":
                    mode = "busy-3"
                    current_order["amount"] = int(msg_in)
                    embed = discord.Embed(title="新增訂單", description="已新增！請確認下方訂單內容是否正確。", color=0x14E073)
                    embed.set_footer(text=time_stamp)
                    final_msg.append(embed)
                    embed = discord.Embed(title="訂單內容：`{0}`".format(str(current_order["order_num"])),
                                          description="商品網址：{0}\n商品數量：{1}".format(
                                              str(current_order["url"]), str(current_order["amount"])),
                                          color=0x14E073)
                    embed.set_footer(text=time_stamp)
                    final_msg.append(embed)
                    embed = discord.Embed(title="確認訂單", description="請輸入`y`表示**確認**。或是輸入`n`，以**取消**這次訂單。",
                                          color=0x14E073)
                    final_msg.append(embed)
                else:
                    embed = discord.Embed(title="錯誤：新增訂單", description="請輸入整數。", color=0xf21c1c)
                    embed.set_footer(text=time_stamp)
                    final_msg.append(embed)
            elif msg_in == "y" or "Y":
                music = discord.Activity(type=discord.ActivityType.playing, name="Alpha測試階段")
                await client.change_presence(status=discord.Status.online, activity=music)
                order_txt_path = base_dir + "\\order-database\\" + str(current_order["order_num"]) + ".txt"
                order_txt = open(order_txt_path, mode="a", encoding="utf-8")
                order_txt.write(str(current_order))
                order_txt.close()
                embed = discord.Embed(title="已確認訂單", description="訂單已確認！\n請記得你的訂單編號：**" + current_order["order_num"] +
                                                                 "**，以便後續的確認！", color=0x14E073)
                embed.set_footer(text=time_stamp)
                final_msg.append(embed)
                order_info = order_notifer.new_order_notice(current_order["order_num"])
                mode = "ready"
                current_order = {}
            elif msg_in == "n" or "N":
                music = discord.Activity(type=discord.ActivityType.playing, name="Alpha測試階段")
                await client.change_presence(status=discord.Status.online, activity=music)
                embed = discord.Embed(title="已取消訂單", description="訂單已取消！", color=0x14E073)
                embed.set_footer(text=time_stamp)
                final_msg.append(embed)
                mode = "ready"
                current_order = {}
    for i in range(len(final_msg)):
        await message.channel.send(embed=final_msg[i])
        new_log = str(message.channel) + "/" + str(client.user) + ":\n" + str(final_msg[i]) + "\n\n"
        log_writter.write_log(new_log)
    if order_info != "":
        channel = client.get_channel(942379971345797151)
        await channel.send("<@657519721138094080>", embed=order_info)
        new_log = str(message.channel) + "/" + str(channel) + ":\n" + str(order_info) + "\n\n"
        log_writter.write_log(new_log)
        order_info = ""
    final_msg = []

env_path = "TOKEN.env"
load_dotenv(dotenv_path=os.path.join(base_dir, "TOKEN.env"))
TOKEN = str(os.getenv("TOKEN"))
client.run(TOKEN)
