
"""
订单类型描述
"""
order_type_message = {
    "3": "邀请分成",
    "4": "官方奖金",
    "11": "私密图片",
    "12": "私密图片",
    "21": "音频",
    "22": "音频",
    "31": "私密视频",
    "32": "私密视频",
    "50": "实物商品",
    "51": "虚拟商品",
    "52": "实物商品",
    "53": "虚拟商品",
    "60": "约见",
    "61": "约见",
    "70": "打赏",
    "71": "打赏",
    "80": "微信",
    "81": "微信",
    "90": "悬赏收入",
    "91": "悬赏收入",
}


"""
订单类型的图片url
"""
order_type_image_url = {
    "3": "http://image.ahachat.cn/upload/material/incomTypeImage/icon_sharing.png",
    "4": "http://image.ahachat.cn/upload/material/incomTypeImage/icon_officialBonus.png",
    "11": "http://image.ahachat.cn/upload/material/incomTypeImage/icon_redPhoto.png",
    "12": "http://image.ahachat.cn/upload/material/incomTypeImage/icon_redPhoto.png",
    "21": "http://image.ahachat.cn/upload/material/incomTypeImage/icon_redVoice.png",
    "22": "http://image.ahachat.cn/upload/material/incomTypeImage/icon_redVoice.png",
    "31": "http://image.ahachat.cn/upload/material/incomTypeImage/icon_redVideo.png",
    "32": "http://image.ahachat.cn/upload/material/incomTypeImage/icon_redVideo.png",
    "50": "http://image.ahachat.cn/upload/material/incomTypeImage/icon_barterGoods.png",
    "51": "http://image.ahachat.cn/upload/material/incomTypeImage/icon_virtualGoods.png",
    "52": "http://image.ahachat.cn/upload/material/incomTypeImage/icon_barterGoods.png",
    "53": "http://image.ahachat.cn/upload/material/incomTypeImage/icon_virtualGoods.png",
    "60": "http://image.ahachat.cn/upload/material/incomTypeImage/icon_appointment.png",
    "61": "http://image.ahachat.cn/upload/material/incomTypeImage/icon_appointment.png",
    "70": "http://image.ahachat.cn/upload/material/incomTypeImage/icon_reward.png",
    "71": "http://image.ahachat.cn/upload/material/incomTypeImage/icon_reward.png",
    "80": "http://image.ahachat.cn/upload/material/incomTypeImage/icon_weChatDeal.png",
    "81": "http://image.ahachat.cn/upload/material/incomTypeImage/icon_weChatDeal.png",
    "90": "http://image.ahachat.cn/upload/material/incomTypeImage/icon_reward.png",
    "91": "http://image.ahachat.cn/upload/material/incomTypeImage/icon_reward.png",
}

"""
支付类型描述
"""
payment_type_message = {
    11: "红包照片",
    60: "约见",
    70: "打赏",
    50: "实物商品",
    51: "虚拟商品",
    80: "微信",
    90: "悬赏",
}

"""
订单类型对应的收款类型
"""
payment_pay_type = {
    11: 12,         # 11 发红包 12 收红包照片
    70: 71,         # 70 打赏   71 收赏
    51: 53,         # 51 虚拟商品 53 收虚拟商品
    50: 52,         # 50 实物商品 52 收实物商品
    80: 81,         # 80 买微信   81 收微信
    90: 91,         # 90 发布悬赏 91 收悬赏
    31: 32,         # 31 发红包   32 收红包
}
