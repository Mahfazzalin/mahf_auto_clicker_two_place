from telethon import TelegramClient, events
import time
import threading
import asyncio
import pyautogui

# Your Telegram Bot Token and API credentials
BOT_TOKEN = 'your Bot Token'  # Replace with your Bot Token
API_ID = your API ID  # Replace with your API ID (must be an integer)
API_HASH = 'your API Hash'  # Replace with your API Hash

app = TelegramClient('auto_clicker', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Global variables to control the clicker
is_running = False
clicker_thread = None
log_data = []
click1_pos = (0, 0)
click2_pos = (0, 0)
click1_duration = 0
click2_duration = 0
first_rest_time = 0
second_rest_time = 0
loop_count = 0
cps = 0
user_input_stage = False
user_id = None
current_question_index = 0

questions = [
    "Please provide Click 1 Position (X axis):",
    "Please provide Click 1 Position (Y axis):",
    "Please provide Click 1 Duration (seconds):",
    "Please provide Click 2 Position (X axis):",
    "Please provide Click 2 Position (Y axis):",
    "Please provide Click 2 Duration (seconds):",
    "Please provide First Rest Time (seconds):",
    "Please provide Second Rest Time (seconds):",
    "Please provide Number of loops:",
    "Please provide Clicks per second (CPS):"
]

def log(message):
    """Append message to log data"""
    global log_data
    log_data.append(message)
    print(message)

def clicker():
    global is_running
    interval = 1 / cps
    click1_count = 0
    click2_count = 0

    for loop in range(loop_count):
        if not is_running:
            break

        log(f"Starting loop {loop + 1}/{loop_count}")

        # Click on position 1
        start_time = time.time()
        while time.time() - start_time < click1_duration:
            pyautogui.click(click1_pos)
            click1_count += 1
            log(f"Clicked at {click1_pos}, Total Click 1: {click1_count}")
            time.sleep(interval)
            if not is_running:
                break

        # Rest after Click 1
        log(f"Resting for {first_rest_time} seconds after Click 1.")
        time.sleep(first_rest_time)

        # Click on position 2
        start_time = time.time()
        while time.time() - start_time < click2_duration:
            pyautogui.click(click2_pos)
            click2_count += 1
            log(f"Clicked at {click2_pos}, Total Click 2: {click2_count}")
            time.sleep(interval)
            if not is_running:
                break

        # Rest after Click 2
        log(f"Resting for {second_rest_time} seconds after Click 2.")
        time.sleep(second_rest_time)

        # Send loop details after each loop
        loop_details = (
            f"Loop {loop + 1}/{loop_count} finished.\n"
            f"Total Click 1: {click1_count}\n"
            f"Total Click 2: {click2_count}"
        )
        log(loop_details)

    log("All loops are finished. The bot is stopping clicking.")
    is_running = False

async def send_logs(event):
    """Send the last 5 logs to the user every 20 seconds."""
    while is_running:
        if log_data:
            last_logs = log_data[-5:]  # Get the last 5 logs
            await event.reply("\n".join(last_logs))
        await asyncio.sleep(20)  # Wait for 20 seconds

@app.on(events.NewMessage(pattern='/getready'))
async def get_ready(event):
    global user_input_stage, user_id, current_question_index

    user_input_stage = True
    user_id = event.sender_id
    current_question_index = 0  # Reset question index
    await event.reply(questions[current_question_index])  # Ask the first question

@app.on(events.NewMessage)
async def handle_user_input(event):
    global click1_pos, click1_duration, click2_pos, click2_duration, first_rest_time, second_rest_time, loop_count, cps
    global user_input_stage, user_id, current_question_index  # Add global declaration

    if user_input_stage and event.sender_id == user_id:
        response = event.message.message.strip()  # Get user response
        try:
            if current_question_index == 0:  # Click 1 X Position
                click1_pos = (int(response), click1_pos[1])  # Set X and keep Y
            elif current_question_index == 1:  # Click 1 Y Position
                click1_pos = (click1_pos[0], int(response))  # Set Y
            elif current_question_index == 2:  # Click 1 Duration
                click1_duration = int(response)
            elif current_question_index == 3:  # Click 2 X Position
                click2_pos = (int(response), click2_pos[1])  # Set X and keep Y
            elif current_question_index == 4:  # Click 2 Y Position
                click2_pos = (click2_pos[0], int(response))  # Set Y
            elif current_question_index == 5:  # Click 2 Duration
                click2_duration = int(response)
            elif current_question_index == 6:  # First Rest Time
                first_rest_time = int(response)
            elif current_question_index == 7:  # Second Rest Time
                second_rest_time = int(response)
            elif current_question_index == 8:  # Loop Count
                loop_count = int(response)
            elif current_question_index == 9:  # CPS
                cps = int(response)

            current_question_index += 1  # Move to the next question

            if current_question_index < len(questions):
                await event.reply(questions[current_question_index])  # Ask next question
            else:
                user_input_stage = False  # End user input stage
                await event.reply("Details received:\n"
                                  f"Click 1 Position: {click1_pos}\n"
                                  f"Click 1 Duration: {click1_duration}\n"
                                  f"Click 2 Position: {click2_pos}\n"
                                  f"Click 2 Duration: {click2_duration}\n"
                                  f"First Rest Time: {first_rest_time}\n"
                                  f"Second Rest Time: {second_rest_time}\n"
                                  f"Loop Count: {loop_count}\n"
                                  f"CPS: {cps}\n"
                                  f"Send /startclick to begin clicking and /stopclicking to stop.")
        except Exception as e:
            await event.reply("please read befor enter any value. Enter only Integer.")

@app.on(events.NewMessage(pattern='/startclick'))
async def start_clicker(event):
    global is_running, clicker_thread

    if is_running:
        await event.reply("Clicker is already running.")
        return

    is_running = True
    clicker_thread = threading.Thread(target=clicker)
    clicker_thread.start()

    # Start sending logs every 20 seconds
    threading.Thread(target=send_logs, args=(event,)).start()
    await event.reply("Clicker started.")

@app.on(events.NewMessage(pattern='/stopclicking'))
async def stop_clicker(event):
    global is_running
    is_running = False
    await event.reply("Clicker stopped.")

@app.on(events.NewMessage(pattern='/log'))
async def send_log(event):
    """Send the log file to the user."""
    with open('log.txt', 'w') as log_file:
        log_file.write('\n'.join(log_data))  # Write all log data to log.txt
    await event.reply("Log file created. You can download it here: log.txt")

if __name__ == '__main__':
    app.start()
    print("Bot is running...")
    app.run_until_disconnected()
