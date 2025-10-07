from_=WHATSAPP_FROM,
        body=text,
        to=WHATSAPP_TO
    )
    print("WhatsApp Message SID:", msg.sid)

if __name__ == "__main__":
    send_whatsapp_message("🚀 Test: WhatsApp alert from Market Bot!")
