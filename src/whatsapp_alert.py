from_=FROM_WHATSAPP,
            body=formatted,
            to=TO_WHATSAPP
        )
        print(f"✅ WhatsApp Message Sent: {msg.sid}")
    except Exception as e:
        print(f"❌ Error sending WhatsApp message: {e}")
