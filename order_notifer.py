import discord
import os

client = discord.Client()


def new_order_notice(order_num):
    base_dir = os.path.abspath(os.path.dirname(__file__))
    order_txt_path = base_dir + "\\order-database\\" + str(order_num) + ".txt"
    order_txt = open(order_txt_path, mode="r", encoding="utf-8")
    order_txt_content = eval(str(order_txt.read()))
    embed = discord.Embed(title="新訂單通知", description="訂單編號：" + str(order_num), color=0x25AEF4)
    embed.add_field(name="訂單提出者", value=order_txt_content["author"], inline=False)
    embed.add_field(name="商品連結", value=order_txt_content["url"], inline=False)
    embed.add_field(name="商品數量", value=order_txt_content["amount"], inline=False)
    return embed
